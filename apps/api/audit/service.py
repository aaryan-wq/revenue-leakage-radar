import logging
import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy import update
from sqlalchemy.orm import Session

from core.data_tiers import (
    get_audit_data_tier,
    get_audit_data_tier_from_uploads,
    missing_recommended_entities,
    missing_recommended_files,
    tier_0_complete,
)
from core.canonical_entities import CanonicalEntity, entities_from_uploaded_files
from core.enums import (
    AuditStatus,
    PROCESSING_STATUSES,
    SCAN_PROCESSING_STATUSES,
    DataTier,
    FileType,
    UploadStatus,
)

_INGESTED_UPLOAD_STATUSES = frozenset(
    {
        UploadStatus.UPLOADED.value,
        UploadStatus.PURGED.value,
    }
)
from models import Audit, Company

logger = logging.getLogger(__name__)


def create_audit(db: Session) -> Audit:
    audit = Audit(
        session_token=secrets.token_urlsafe(32),
        status=AuditStatus.CREATED.value,
        audit_type="free",
        is_anonymous=True,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def get_audit_by_id(db: Session, audit_id: uuid.UUID) -> Audit | None:
    return db.query(Audit).filter(Audit.id == audit_id).first()


def get_audit_by_session_token(db: Session, session_token: str) -> Audit | None:
    return db.query(Audit).filter(Audit.session_token == session_token).first()


def get_uploaded_file_types(audit: Audit) -> set[FileType]:
    """File types successfully received for this audit (including post-ingestion purged CSVs)."""
    return {
        FileType(upload.file_type)
        for upload in audit.uploads
        if upload.status in _INGESTED_UPLOAD_STATUSES
    }


def get_missing_required_file_types(audit: Audit) -> list[FileType]:
    """Deprecated, no hard-required files. Returns empty list."""
    return []


def has_billing_upload(audit: Audit) -> bool:
    return bool(get_uploaded_file_types(audit))


def get_missing_recommended_file_types(audit: Audit) -> list[FileType]:
    uploaded = get_uploaded_file_types(audit)
    return missing_recommended_files(uploaded)


def get_available_entities_for_audit(audit: Audit) -> set[CanonicalEntity]:
    if audit.available_entities:
        return {CanonicalEntity(entity) for entity in audit.available_entities}
    return entities_from_uploaded_files(get_uploaded_file_types(audit))


def get_missing_entities_for_audit(audit: Audit) -> list[CanonicalEntity]:
    return missing_recommended_entities(get_available_entities_for_audit(audit))


def get_missing_recommended_entities_for_audit(audit: Audit) -> list[CanonicalEntity]:
    return missing_recommended_entities(get_available_entities_for_audit(audit))


def get_coverage_analysis_for_audit(audit: Audit) -> dict:
    from verification.coverage import analyze_coverage

    available = get_available_entities_for_audit(audit)
    uploaded = get_uploaded_file_types(audit)
    return analyze_coverage(
        available_entities=available,
        uploaded_file_types=uploaded,
    )


def get_audit_data_tier_for_audit(audit: Audit) -> DataTier:
    if audit.available_entities:
        return get_audit_data_tier({CanonicalEntity(entity) for entity in audit.available_entities})
    return get_audit_data_tier_from_uploads(get_uploaded_file_types(audit))


def link_audit_to_user(db: Session, audit: Audit, clerk_user_id: str) -> Audit:
    if audit.clerk_user_id and audit.clerk_user_id != clerk_user_id:
        raise PermissionError("Audit is already linked to another user.")
    if audit.clerk_user_id == clerk_user_id:
        return audit
    from analytics.audit_summary import link_user_updates

    link_user_updates(db, audit, clerk_user_id)
    audit.session_token = secrets.token_urlsafe(32)
    db.commit()
    db.refresh(audit)
    return audit


def transition_audit_status(db: Session, audit: Audit, new_status: AuditStatus) -> Audit:
    audit.status = new_status.value
    db.commit()
    db.refresh(audit)
    logger.info("Audit %s status -> %s", audit.id, new_status.value)
    return audit


def try_claim_audit_status(
    db: Session,
    audit_id: uuid.UUID,
    *,
    allowed_from: frozenset[AuditStatus],
    new_status: AuditStatus,
) -> bool:
    """Atomically transition audit status when still in an allowed state."""
    result = db.execute(
        update(Audit)
        .where(
            Audit.id == audit_id,
            Audit.status.in_([status.value for status in allowed_from]),
        )
        .values(status=new_status.value)
    )
    db.commit()
    return result.rowcount > 0


def is_processing(audit: Audit) -> bool:
    try:
        status = AuditStatus(audit.status)
    except ValueError:
        return False
    return status in PROCESSING_STATUSES


def can_trigger_ingestion(audit: Audit) -> tuple[bool, str | None]:
    uploaded = get_uploaded_file_types(audit)
    if not uploaded:
        return False, "Upload at least one billing export to continue."

    try:
        current = AuditStatus(audit.status)
        if current == AuditStatus.READY_FOR_SCAN:
            return False, "Ingestion already completed."
        if current in PROCESSING_STATUSES:
            return False, "Ingestion is already in progress."
        if current in (
            AuditStatus.VALIDATION_FAILED,
            AuditStatus.PROCESSING_FAILED,
        ):
            return True, None
    except ValueError:
        pass

    return True, None


def trigger_ingestion(db: Session, audit: Audit) -> None:
    from workers.tasks.ingestion import run_ingestion_task

    can_run, reason = can_trigger_ingestion(audit)
    if not can_run:
        raise ValueError(reason or "Cannot start ingestion")

    claimed = try_claim_audit_status(
        db,
        audit.id,
        allowed_from=frozenset(
            {
                AuditStatus.CREATED,
                AuditStatus.UPLOADING,
                AuditStatus.VALIDATION_FAILED,
                AuditStatus.PROCESSING_FAILED,
            }
        ),
        new_status=AuditStatus.MAPPING,
    )
    if not claimed:
        db.refresh(audit)
        can_run, reason = can_trigger_ingestion(audit)
        if not can_run:
            raise ValueError(reason or "Cannot start ingestion")
        raise ValueError("Ingestion is already in progress.")

    run_ingestion_task.delay(str(audit.id))


def get_validation_response(audit: Audit) -> dict:
    from core.enums import ValidationResult

    report = audit.validation_report or {}
    issues = report.get("issues", [])
    blocking_count = sum(1 for i in issues if i.get("severity") == "blocking")
    warning_count = sum(1 for i in issues if i.get("severity") == "warning")

    can_proceed = audit.validation_result in (
        ValidationResult.READY.value,
        ValidationResult.WARNINGS.value,
    ) and audit.status in (
        AuditStatus.READY_FOR_SCAN.value,
        AuditStatus.PROCESSING_FAILED.value,
    )

    return {
        "audit_id": str(audit.id),
        "status": audit.status,
        "platform": audit.platform,
        "column_mappings": audit.column_mappings or {},
        "validation_result": audit.validation_result,
        "validation_report": report,
        "ingestion_error": audit.ingestion_error,
        "can_proceed_to_scan": can_proceed,
        "summary": {
            "blocking_count": blocking_count,
            "warning_count": warning_count,
            "issue_count": len(issues),
        },
    }


def get_scan_response(audit: Audit) -> dict:
    scan_report = audit.scan_report or {}
    return {
        "audit_id": str(audit.id),
        "status": audit.status,
        "scan_report": scan_report,
        "scan_error": audit.scan_error,
        "finding_count": scan_report.get("finding_count", 0),
        "recoverable_arr": scan_report.get("recoverable_arr", "0"),
        "rules_completed": scan_report.get("rules_completed", 0),
        "rules_total": scan_report.get("rules_total", 0),
        "overall_confidence": scan_report.get("overall_confidence"),
    }


def can_trigger_scan(audit: Audit) -> tuple[bool, str | None]:
    try:
        current = AuditStatus(audit.status)
    except ValueError:
        return False, "Invalid audit status."

    from core.enums import SCAN_PROCESSING_STATUSES, ValidationResult

    if current not in (AuditStatus.READY_FOR_SCAN, AuditStatus.PROCESSING_FAILED):
        if current in SCAN_PROCESSING_STATUSES:
            return False, "Scan is already in progress."
        if current == AuditStatus.COMPLETED:
            return False, "Scan already completed."
        return False, "Audit is not ready for scan."

    if audit.validation_result == ValidationResult.BLOCKING.value:
        return False, "Validation has blocking errors."

    return True, None


STALE_SCAN_SECONDS = 300
EAGER_STALE_SCAN_SECONDS = 60
STALE_INGESTION_SECONDS = 300
EAGER_STALE_INGESTION_SECONDS = 60


def _is_stale(updated_at: datetime | None, *, eager_seconds: int, default_seconds: int) -> bool:
    from core.config import settings

    if updated_at is None or not isinstance(updated_at, datetime):
        return True
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    stale_after = eager_seconds if settings.celery_task_always_eager else default_seconds
    age_seconds = (datetime.now(timezone.utc) - updated_at).total_seconds()
    return age_seconds > stale_after


def recover_stale_ingestion_if_needed(db: Session, audit: Audit) -> bool:
    try:
        current = AuditStatus(audit.status)
    except ValueError:
        return False

    if current not in PROCESSING_STATUSES:
        return False

    if not _is_stale(
        audit.updated_at,
        eager_seconds=EAGER_STALE_INGESTION_SECONDS,
        default_seconds=STALE_INGESTION_SECONDS,
    ):
        return False

    audit.status = AuditStatus.PROCESSING_FAILED.value
    audit.ingestion_error = audit.ingestion_error or "Ingestion timed out. Please try again."
    db.commit()
    logger.info("Recovered stale ingestion state for audit %s", audit.id)
    return True


def recover_stale_scan_if_needed(db: Session, audit: Audit) -> bool:
    """Reset orphaned scanning state left by interrupted workers or API reloads."""
    try:
        current = AuditStatus(audit.status)
    except ValueError:
        return False

    if current not in SCAN_PROCESSING_STATUSES:
        return False

    if audit.updated_at is None:
        is_stale = True
    else:
        is_stale = _is_stale(
            audit.updated_at,
            eager_seconds=EAGER_STALE_SCAN_SECONDS,
            default_seconds=STALE_SCAN_SECONDS,
        )

    if not is_stale:
        return False

    audit.status = AuditStatus.READY_FOR_SCAN.value
    audit.scan_error = None
    db.commit()
    logger.info("Recovered stale scan state for audit %s", audit.id)
    return True


def trigger_verification(db: Session, audit: Audit) -> None:
    from workers.tasks.verification import run_verification_task

    recover_stale_scan_if_needed(db, audit)
    db.refresh(audit)

    can_run, reason = can_trigger_scan(audit)
    if can_run:
        audit.scan_error = None
        claimed = try_claim_audit_status(
            db,
            audit.id,
            allowed_from=frozenset({AuditStatus.READY_FOR_SCAN, AuditStatus.PROCESSING_FAILED}),
            new_status=AuditStatus.SCANNING,
        )
        if claimed:
            run_verification_task.delay(str(audit.id))
        return

    try:
        current = AuditStatus(audit.status)
    except ValueError as exc:
        raise ValueError(reason or "Cannot start verification scan") from exc

    if current in SCAN_PROCESSING_STATUSES or current == AuditStatus.COMPLETED:
        return

    raise ValueError(reason or "Cannot start verification scan")


def get_scan_response_with_recovery(db: Session, audit: Audit) -> dict:
    recover_stale_scan_if_needed(db, audit)
    db.refresh(audit)
    return get_scan_response(audit)


def is_scan_processing(audit: Audit) -> bool:
    from core.enums import SCAN_PROCESSING_STATUSES

    try:
        status = AuditStatus(audit.status)
    except ValueError:
        return False
    return status in SCAN_PROCESSING_STATUSES


NON_DELETABLE_STATUSES: set[AuditStatus] = (
    PROCESSING_STATUSES
    | SCAN_PROCESSING_STATUSES
    | {
        AuditStatus.UPLOADING,
        AuditStatus.CREATED,
        AuditStatus.PAYMENT_PENDING,
    }
)

PERSISTENT_AUDIT_STATUSES: set[AuditStatus] = {
    AuditStatus.COMPLETED,
    AuditStatus.PAYMENT_PENDING,
}


def can_abandon_audit(audit: Audit) -> tuple[bool, str | None]:
    if audit.report is not None and audit.report.purchased:
        return False, "Purchased reports cannot be discarded."

    try:
        status = AuditStatus(audit.status)
    except ValueError:
        return False, "Invalid audit status."

    if status in PERSISTENT_AUDIT_STATUSES:
        return False, None

    return True, None


def _destroy_audit_data(db: Session, audit: Audit) -> None:
    from canonical.transformer import clear_canonical_data
    from upload.cleanup import purge_audit_upload_files_by_audit

    company_id = audit.company_id
    purge_audit_upload_files_by_audit(db, audit)

    if audit.report is not None:
        db.delete(audit.report)

    db.delete(audit)
    db.flush()

    if company_id:
        remaining = db.query(Audit).filter(Audit.company_id == company_id).count()
        if remaining == 0:
            clear_canonical_data(db, company_id)
            db.query(Company).filter(Company.id == company_id).delete(synchronize_session=False)


def abandon_audit_session(db: Session, audit: Audit) -> bool:
    """Discard an in-progress audit and all associated billing data.

    Returns True when the audit was deleted. Completed or purchased audits are
    preserved and return False without error.
    """
    can_abandon, reason = can_abandon_audit(audit)
    if not can_abandon:
        if reason is None:
            return False
        raise ValueError(reason)

    from analytics.tracking import track_audit_cancelled

    track_audit_cancelled(audit)
    _destroy_audit_data(db, audit)
    db.commit()
    logger.info("Abandoned audit session %s", audit.id)
    return True


def delete_user_audit(db: Session, audit: Audit, clerk_user_id: str) -> None:
    if audit.clerk_user_id != clerk_user_id:
        raise PermissionError("You do not have permission to delete this audit.")

    try:
        status = AuditStatus(audit.status)
    except ValueError:
        raise ValueError("Invalid audit status.")

    if status in NON_DELETABLE_STATUSES:
        raise ValueError("Cannot delete an audit while processing is in progress.")

    _destroy_audit_data(db, audit)
    db.commit()
    logger.info("Deleted audit %s for user %s", audit.id, clerk_user_id)
