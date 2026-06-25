import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from audit.service import (
    create_audit,
    get_audit_by_id,
    get_missing_required_file_types,
)
from auth.dependencies import verify_audit_session
from core.config import settings
from core.enums import AuditStatus, FileType, UploadStatus
from database.session import get_db
from models import Audit
from schemas import AuditCreateResponse, AuditStatusResponse, UploadResponse
from upload.service import save_upload

logger = logging.getLogger(__name__)

router = APIRouter(tags=["audit"])


def _upload_to_response(upload) -> UploadResponse:
    return UploadResponse(
        id=upload.id,
        audit_id=upload.audit_id,
        file_type=FileType(upload.file_type),
        original_filename=upload.original_filename,
        file_size=upload.file_size,
        status=UploadStatus(upload.status),
        created_at=upload.created_at,
    )


@router.post("/audit", response_model=AuditCreateResponse, status_code=status.HTTP_201_CREATED)
def create_audit_session(db: Session = Depends(get_db)) -> AuditCreateResponse:
    audit = create_audit(db)
    logger.info("Created audit session %s", audit.id)
    return AuditCreateResponse(
        audit_id=audit.id,
        session_token=audit.session_token,
        status=AuditStatus(audit.status),
    )


@router.get("/audit/{audit_id}", response_model=AuditStatusResponse)
def get_audit_status(
    audit_id: UUID,
    audit: Audit = Depends(verify_audit_session),
) -> AuditStatusResponse:
    missing = get_missing_required_file_types(audit)
    return AuditStatusResponse(
        audit_id=audit.id,
        status=AuditStatus(audit.status),
        uploads=[_upload_to_response(u) for u in audit.uploads],
        required_files_present=len(missing) == 0,
        missing_file_types=missing,
    )


@router.post(
    "/audit/{audit_id}/upload",
    response_model=list[UploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_files(
    files: list[UploadFile] = File(...),
    audit: Audit = Depends(verify_audit_session),
    db: Session = Depends(get_db),
) -> list[UploadResponse]:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required.",
        )

    results = []
    for file in files:
        upload = await save_upload(db, audit, file)
        results.append(_upload_to_response(upload))
        logger.info(
            "Uploaded file %s for audit %s (%s bytes)",
            upload.original_filename,
            audit.id,
            upload.file_size,
        )

    return results
