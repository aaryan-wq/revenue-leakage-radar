import logging
import secrets
import uuid

from sqlalchemy.orm import Session

from core.enums import AuditStatus, PROCESSING_STATUSES, FileType, REQUIRED_BILLING_FILE_TYPES
from models import Audit

logger = logging.getLogger(__name__)


def create_audit(db: Session) -> Audit:
    audit = Audit(
        session_token=secrets.token_urlsafe(32),
        status=AuditStatus.CREATED.value,
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
    return {FileType(upload.file_type) for upload in audit.uploads if upload.status == "uploaded"}


def get_missing_required_file_types(audit: Audit) -> list[FileType]:
    uploaded = get_uploaded_file_types(audit)
    return sorted(REQUIRED_BILLING_FILE_TYPES - uploaded, key=lambda ft: ft.value)


def link_audit_to_user(db: Session, audit: Audit, clerk_user_id: str) -> Audit:
    audit.clerk_user_id = clerk_user_id
    db.commit()
    db.refresh(audit)
    return audit


def transition_audit_status(db: Session, audit: Audit, new_status: AuditStatus) -> Audit:
    audit.status = new_status.value
    db.commit()
    db.refresh(audit)
    logger.info("Audit %s status -> %s", audit.id, new_status.value)
    return audit


def is_processing(audit: Audit) -> bool:
    try:
        status = AuditStatus(audit.status)
    except ValueError:
        return False
    return status in PROCESSING_STATUSES


def can_trigger_ingestion(audit: Audit) -> tuple[bool, str | None]:
    uploaded = get_uploaded_file_types(audit)
    missing = REQUIRED_BILLING_FILE_TYPES - uploaded
    if missing:
        return False, "Required billing files are not all uploaded."

    try:
        current = AuditStatus(audit.status)
        if current == AuditStatus.READY_FOR_SCAN:
            return False, "Ingestion already completed."
        if current in PROCESSING_STATUSES:
            return False, "Ingestion is already in progress."
    except ValueError:
        pass

    return True, None


def trigger_ingestion(db: Session, audit: Audit) -> None:
    from workers.tasks.ingestion import run_ingestion_task

    can_run, reason = can_trigger_ingestion(audit)
    if not can_run:
        raise ValueError(reason or "Cannot start ingestion")

    run_ingestion_task.delay(str(audit.id))


def get_validation_response(audit: Audit) -> dict:
    from core.enums import ValidationResult

    report = audit.validation_report or {}
    issues = report.get("issues", [])
    blocking_count = sum(1 for i in issues if i.get("severity") == "blocking")
    warning_count = sum(1 for i in issues if i.get("severity") == "warning")

    can_proceed = (
        audit.validation_result in (ValidationResult.READY.value, ValidationResult.WARNINGS.value)
        and audit.status == AuditStatus.READY_FOR_SCAN.value
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

    if current != AuditStatus.READY_FOR_SCAN:
        if current in SCAN_PROCESSING_STATUSES:
            return False, "Scan is already in progress."
        if current == AuditStatus.COMPLETED:
            return False, "Scan already completed."
        return False, "Audit is not ready for scan."

    if audit.validation_result == ValidationResult.BLOCKING.value:
        return False, "Validation has blocking errors."

    return True, None


def trigger_verification(db: Session, audit: Audit) -> None:
    from workers.tasks.verification import run_verification_task

    can_run, reason = can_trigger_scan(audit)
    if not can_run:
        raise ValueError(reason or "Cannot start verification scan")

    run_verification_task.delay(str(audit.id))


def is_scan_processing(audit: Audit) -> bool:
    from core.enums import SCAN_PROCESSING_STATUSES

    try:
        status = AuditStatus(audit.status)
    except ValueError:
        return False
    return status in SCAN_PROCESSING_STATUSES
