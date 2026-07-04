import logging
import uuid

from sqlalchemy.orm import Session

from analytics import audit_summary, tracking
from audit.service import transition_audit_status
from core.enums import AuditStatus
from findings.service import clear_findings, persist_findings
from models import Audit
from reports.service import upsert_report
from verification.attribution import sum_primary_recoverable_arr
from verification.calculator.financial import weighted_confidence
from verification.context import load_audit_context
from verification.coverage import analyze_coverage_from_context
from verification.engine.runner import run_engine
from verification.types import ScanReport

logger = logging.getLogger(__name__)


def run_verification_engine(db: Session, audit: Audit) -> ScanReport:
    if not audit.company_id:
        raise ValueError("Audit has no company_id, run ingestion first")

    transition_audit_status(db, audit, AuditStatus.SCANNING)
    audit.scan_error = None
    audit_summary.mark_verification_started(db, audit)
    db.commit()

    started_at = tracking.track_verification_started(audit)
    ctx = load_audit_context(db, audit.id, audit.company_id)
    clear_findings(db, audit.id)

    attributed, report = run_engine(ctx)
    primary = [finding for finding in attributed if finding.attribution == "primary"]
    secondary_count = sum(1 for finding in attributed if finding.attribution == "secondary")
    recoverable = sum_primary_recoverable_arr(attributed)
    overall_conf = weighted_confidence(primary)
    coverage = analyze_coverage_from_context(ctx)
    coverage_score = coverage.get("estimated_confidence")

    persisted = persist_findings(db, audit.id, attributed)
    transition_audit_status(db, audit, AuditStatus.GENERATING_REPORT)
    upsert_report(db, audit.id, recoverable, len(persisted), overall_conf)

    report = report.model_copy(
        update={
            "finding_count": len(persisted),
            "recoverable_arr": str(recoverable),
            "overall_confidence": str(overall_conf) if overall_conf is not None else None,
        }
    )

    audit.scan_report = report.to_dict()
    audit.scan_error = None
    tracking.track_verification_completed(
        db,
        audit,
        report=report,
        primary_findings=primary,
        secondary_count=secondary_count,
        coverage_score=coverage_score,
        started_at=started_at,
    )
    transition_audit_status(db, audit, AuditStatus.COMPLETED)
    db.commit()

    logger.info(
        "Verification complete for audit %s: %d findings, ARR %s",
        audit.id,
        len(persisted),
        recoverable,
    )
    return report


def run_verification_pipeline(db: Session, audit_id: uuid.UUID) -> None:
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise ValueError(f"Audit not found: {audit_id}")

    try:
        run_verification_engine(db, audit)
    except Exception as exc:
        logger.exception("Verification failed for audit %s", audit_id)
        db.rollback()
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if audit is not None:
            audit.scan_error = "Verification scan failed. Please try again."
            transition_audit_status(db, audit, AuditStatus.PROCESSING_FAILED)
            tracking.track_verification_failed(audit, error=str(exc))
            db.commit()
        raise exc
