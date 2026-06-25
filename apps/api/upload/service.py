import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from core.config import settings
from core.enums import FILENAME_TO_FILE_TYPE, AuditStatus, FileType, UploadStatus
from models import Audit, Upload


def detect_file_type(filename: str) -> FileType:
    stem = Path(filename).stem.lower()
    name = filename.lower()
    return FILENAME_TO_FILE_TYPE.get(stem, FILENAME_TO_FILE_TYPE.get(name, FileType.UNKNOWN))


def validate_csv_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename.",
        )
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only CSV files are accepted. Received: {file.filename}",
        )


async def save_upload(
    db: Session,
    audit: Audit,
    file: UploadFile,
) -> Upload:
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

    existing = (
        db.query(Upload)
        .filter(Upload.audit_id == audit.id, Upload.file_type == file_type.value)
        .first()
    )
    if existing:
        old_path = Path(existing.storage_path)
        if old_path.exists():
            old_path.unlink()
        existing.original_filename = file.filename
        existing.storage_path = str(storage_path)
        existing.file_size = file_size
        existing.status = UploadStatus.UPLOADED.value
        db.commit()
        db.refresh(existing)
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
    db.commit()
    db.refresh(upload)
    return upload
