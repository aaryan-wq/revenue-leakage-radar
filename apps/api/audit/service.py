import secrets
import uuid

from sqlalchemy.orm import Session

from core.enums import AuditStatus, REQUIRED_BILLING_FILE_TYPES, FileType
from models import Audit, Upload


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
