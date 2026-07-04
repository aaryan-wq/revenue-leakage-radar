import logging
import shutil
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from core.config import settings
from core.enums import UploadStatus
from models import Audit, Upload

logger = logging.getLogger(__name__)


def purge_audit_upload_files(db: Session, audit_id: uuid.UUID) -> int:
    """Delete raw CSV files from disk and mark upload rows as purged."""
    uploads = db.query(Upload).filter(Upload.audit_id == audit_id).all()
    purged_count = 0

    for upload in uploads:
        if upload.status == UploadStatus.PURGED.value:
            continue
        path = Path(upload.storage_path)
        if path.exists():
            try:
                path.unlink()
                purged_count += 1
            except OSError:
                logger.exception("Failed to delete upload file %s", path)
        upload.status = UploadStatus.PURGED.value

    audit_dir = Path(settings.upload_dir) / str(audit_id)
    if audit_dir.exists():
        try:
            shutil.rmtree(audit_dir, ignore_errors=True)
        except OSError:
            logger.exception("Failed to remove audit upload directory %s", audit_dir)

    if uploads:
        db.commit()

    if purged_count:
        logger.info("Purged %d upload file(s) for audit %s", purged_count, audit_id)

    return purged_count


def purge_audit_upload_files_by_audit(db: Session, audit: Audit) -> int:
    return purge_audit_upload_files(db, audit.id)
