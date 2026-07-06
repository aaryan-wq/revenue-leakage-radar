"""Ingestion pipeline orchestration, adapters → validation → normalization."""

import logging

from sqlalchemy.orm import Session

from adapters.registry import build_adapter_output
from ai.mapping import detect_and_map_uploads
from audit.service import transition_audit_status
from core.data_tiers import get_audit_data_tier_from_entities, get_audit_data_tier_from_uploads
from core.enums import AuditStatus, FileType
from ingestion.normalizer import normalize_to_canonical
from ingestion.types import IngestionContext
from models import Audit
from validation.parser import load_uploaded_frames
from validation.service import run_validation

logger = logging.getLogger(__name__)


def run_ingestion_pipeline(db: Session, audit: Audit) -> None:
    from upload.cleanup import purge_audit_upload_files_by_audit
    from analytics import audit_summary, tracking

    tracking.track_validation_started(audit)

    uploads = [u for u in audit.uploads if u.status == "uploaded"]
    uploaded_types = {FileType(u.file_type) for u in uploads}

    try:
        transition_audit_status(db, audit, AuditStatus.MAPPING)
        platform, mappings = detect_and_map_uploads(uploads)
        audit_summary.sync_billing_platform(db, audit, platform.value)
        audit.column_mappings = mappings
        db.commit()

        transition_audit_status(db, audit, AuditStatus.VALIDATING)
        frames = load_uploaded_frames(uploads, mappings)
        validation_report = run_validation(frames, uploaded_types)
        audit.validation_report = validation_report.to_dict()
        audit.validation_result = validation_report.result().value
        audit.data_tier = get_audit_data_tier_from_uploads(uploaded_types).value
        audit.uploaded_file_types = sorted(ft.value for ft in uploaded_types)
        db.commit()

        if validation_report.has_blocking:
            transition_audit_status(db, audit, AuditStatus.VALIDATION_FAILED)
            audit.ingestion_error = "Validation failed with blocking errors."
            tracking.track_validation_failed(audit, reason="blocking_errors")
            db.commit()
            return

        transition_audit_status(db, audit, AuditStatus.NORMALIZING)
        adapter_output = build_adapter_output(platform, mappings, uploaded_types)
        ctx = IngestionContext(
            audit_id=str(audit.id),
            platform=platform,
            column_mappings=mappings,
            frames=frames,
            validation_report=validation_report,
            uploaded_file_types=uploaded_types,
            available_entities=adapter_output.detected_entities,
        )
        transform_result = normalize_to_canonical(db, audit, ctx)
        audit.data_tier = get_audit_data_tier_from_entities(ctx.available_entities).value

        validation_payload = dict(audit.validation_report or {})
        validation_payload["row_errors"] = transform_result.to_dict()["row_errors"]
        validation_payload["canonical_counts"] = transform_result.counts
        validation_payload["available_entities"] = audit.available_entities or []
        audit.validation_report = validation_payload

        audit_summary.sync_data_presence(db, audit)
        transition_audit_status(db, audit, AuditStatus.READY_FOR_SCAN)
        audit.ingestion_error = None
        db.commit()
        tracking.track_validation_completed(audit)
        purge_audit_upload_files_by_audit(db, audit)
        logger.info(
            "audit_milestone audit_id=%s milestone=ingestion_complete "
            "customers=%s subscriptions=%s invoices=%s line_items=%s row_errors=%s",
            audit.id,
            transform_result.counts.get("customers", 0),
            transform_result.counts.get("subscriptions", 0),
            transform_result.counts.get("invoices", 0),
            transform_result.counts.get("invoice_line_items", 0),
            len(transform_result.row_errors),
        )

    except Exception as exc:
        logger.exception("Ingestion failed for audit %s", audit.id)
        audit.ingestion_error = "Processing failed. Please try again."
        transition_audit_status(db, audit, AuditStatus.PROCESSING_FAILED)
        tracking.track_validation_failed(audit, reason=str(exc))
        db.commit()
        raise exc
