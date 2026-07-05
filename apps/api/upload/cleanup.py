import logging
import uuid

from sqlalchemy.orm import Session

from core.enums import UploadStatus
from models import Audit, Upload
from storage.factory import get_storage
from storage.reader import storage_exists

logger = logging.getLogger(__name__)


def purge_audit_upload_files(db: Session, audit_id: uuid.UUID) -> int:
    """Delete raw CSV files from storage and mark upload rows as purged."""
    uploads = db.query(Upload).filter(Upload.audit_id == audit_id).all()
    purged_count = 0
    storage = get_storage()

    for upload in uploads:
        if upload.status == UploadStatus.PURGED.value:
            continue
        if storage_exists(upload.storage_path):
            try:
                storage.delete(upload.storage_path, bucket="uploads")
                purged_count += 1
            except Exception:
                logger.exception("Failed to delete upload file %s", upload.storage_path)
        upload.status = UploadStatus.PURGED.value

    if uploads:
        db.commit()

    if purged_count:
        logger.info("Purged %d upload file(s) for audit %s", purged_count, audit_id)

    return purged_count


def purge_audit_upload_files_by_audit(db: Session, audit: Audit) -> int:
    return purge_audit_upload_files(db, audit.id)
