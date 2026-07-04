import logging
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from adapters.generic.adapter import GenericAdapter
from audit.service import get_uploaded_file_types, is_processing, is_scan_processing
from core.canonical_entities import entities_from_uploaded_files
from core.config import settings
from core.data_tiers import get_audit_data_tier_from_uploads
from core.enums import AuditStatus, FileType, UploadStatus
from models import Audit, Upload


_generic_adapter = GenericAdapter()


def detect_file_type(filename: str) -> FileType:
    return _generic_adapter.classify_upload(filename)


def validate_csv_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename.",
        )
    filename = file.filename.replace("\x00", "")
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename.",
        )
    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only CSV files are accepted. Received: {file.filename}",
        )


async def save_upload(
    db: Session,
    audit: Audit,
    file: UploadFile,
) -> Upload:
    if is_processing(audit) or is_scan_processing(audit):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot upload files while processing is in progress.",
        )

    validate_csv_file(file)

    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File is empty: {file.filename}",
        )

    if file_size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb} MB.",
        )

    file_type = detect_file_type(file.filename)
    if file_type == FileType.UNKNOWN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Could not detect file type from filename: {file.filename}. "
                "Use standard names like subscriptions.csv, invoices.csv, etc."
            ),
        )

    upload_dir = Path(settings.upload_dir) / str(audit.id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    storage_filename = f"{file_type.value}_{uuid.uuid4().hex}.csv"
    storage_path = upload_dir / storage_filename
    storage_path.write_bytes(content)

    replaced = False
    existing = (
        db.query(Upload)
        .filter(Upload.audit_id == audit.id, Upload.file_type == file_type.value)
        .first()
    )
    if existing:
        replaced = True
        old_path = Path(existing.storage_path)
        if old_path.exists():
            old_path.unlink()
        existing.original_filename = file.filename
        existing.storage_path = str(storage_path)
        existing.file_size = file_size
        existing.status = UploadStatus.UPLOADED.value
        _reset_ingestion_state(db, audit)
        db.commit()
        db.refresh(existing)
        from analytics import audit_summary, tracking

        audit_summary.sync_upload_counts(db, audit)
        db.commit()
        tracking.track_upload_completed(
            audit,
            file_id=str(existing.id),
            original_filename=file.filename,
            detected_file_type=file_type.value,
            file_size_bytes=file_size,
            replaced=True,
        )
        return existing

    upload = Upload(
        audit_id=audit.id,
        file_type=file_type.value,
        original_filename=file.filename,
        storage_path=str(storage_path),
        file_size=file_size,
        status=UploadStatus.UPLOADED.value,
    )
    db.add(upload)

    audit.status = AuditStatus.UPLOADING.value
    _reset_ingestion_state(db, audit)
    db.commit()
    db.refresh(upload)

    from analytics import audit_summary, tracking

    audit_summary.sync_upload_counts(db, audit)
    db.commit()
    tracking.track_upload_completed(
        audit,
        file_id=str(upload.id),
        original_filename=file.filename,
        detected_file_type=file_type.value,
        file_size_bytes=file_size,
        replaced=False,
    )
    return upload


def _clear_audit_analysis_artifacts(db: Session, audit: Audit) -> None:
    from decimal import Decimal

    from models import Finding, Report

    db.query(Finding).filter(Finding.audit_id == audit.id).delete(synchronize_session=False)
    report = db.query(Report).filter(Report.audit_id == audit.id).first()
    if report:
        report.recoverable_arr = Decimal("0")
        report.finding_count = 0
        report.confidence = None
        report.purchased = False
        report.generated_at = None


def _reset_ingestion_state(db: Session, audit: Audit) -> None:
    audit.platform = None
    audit.column_mappings = None
    audit.validation_report = None
    audit.validation_result = None
    audit.ingestion_error = None
    audit.scan_report = None
    audit.scan_error = None
    if audit.status in (
        AuditStatus.READY_FOR_SCAN.value,
        AuditStatus.VALIDATION_FAILED.value,
        AuditStatus.PROCESSING_FAILED.value,
        AuditStatus.COMPLETED.value,
        AuditStatus.SCANNING.value,
        AuditStatus.GENERATING_REPORT.value,
    ):
        audit.status = AuditStatus.UPLOADING.value
        _clear_audit_analysis_artifacts(db, audit)


def maybe_auto_trigger_ingestion(db: Session, audit: Audit) -> None:
    """Ingestion starts when the user continues to validation, not on each upload."""
    return


def delete_upload(db: Session, audit: Audit, upload_id: uuid.UUID) -> None:
    if is_processing(audit) or is_scan_processing(audit):
        raise ValueError("Cannot remove files while processing is in progress.")

    upload = (
        db.query(Upload)
        .filter(Upload.audit_id == audit.id, Upload.id == upload_id)
        .first()
    )
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found.",
        )

    original_filename = upload.original_filename
    file_id = str(upload.id)

    path = Path(upload.storage_path)
    if path.exists():
        try:
            path.unlink()
        except OSError:
            logger.exception("Failed to delete upload file %s", path)

    db.delete(upload)
    db.flush()

    _reset_ingestion_state(db, audit)
    remaining_types = get_uploaded_file_types(audit)
    audit.uploaded_file_types = sorted(file_type.value for file_type in remaining_types)
    audit.available_entities = sorted(
        entity.value for entity in entities_from_uploaded_files(remaining_types)
    )
    audit.data_tier = get_audit_data_tier_from_uploads(remaining_types).value

    if remaining_types:
        audit.status = AuditStatus.UPLOADING.value
    else:
        audit.status = AuditStatus.CREATED.value

    from analytics import audit_summary, tracking

    audit_summary.sync_upload_counts(db, audit)
    db.commit()
    tracking.track_upload_removed(audit, file_id=file_id, original_filename=original_filename)
    db.refresh(audit)
    logger.info("Deleted upload %s from audit %s", upload_id, audit.id)
