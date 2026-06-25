import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from audit.service import (
    create_audit,
    get_missing_required_file_types,
    get_scan_response,
    get_validation_response,
    trigger_ingestion,
    trigger_verification,
)
from auth.dependencies import verify_audit_session
from core.enums import AuditStatus, FileType, UploadStatus, ValidationResult
from database.session import get_db
from models import Audit
from schemas import (
    AuditCreateResponse,
    AuditStatusResponse,
    ScanReportResponse,
    ScanResponse,
    UploadResponse,
    ValidateResponse,
    ValidationReportResponse,
)
from upload.service import maybe_auto_trigger_ingestion, save_upload

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
    audit: Audit = Depends(verify_audit_session),
) -> AuditStatusResponse:
    missing = get_missing_required_file_types(audit)
    validation_result = None
    if audit.validation_result:
        try:
            validation_result = ValidationResult(audit.validation_result)
        except ValueError:
            validation_result = None

    return AuditStatusResponse(
        audit_id=audit.id,
        status=AuditStatus(audit.status),
        uploads=[_upload_to_response(u) for u in audit.uploads],
        required_files_present=len(missing) == 0,
        missing_file_types=missing,
        platform=audit.platform,
        validation_result=validation_result,
        can_proceed_to_scan=audit.status == AuditStatus.READY_FOR_SCAN.value,
        ingestion_error=audit.ingestion_error,
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

    db.refresh(audit)
    maybe_auto_trigger_ingestion(db, audit)

    return results


@router.post(
    "/audit/{audit_id}/validate",
    response_model=ValidateResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_validation(
    audit: Audit = Depends(verify_audit_session),
    db: Session = Depends(get_db),
) -> ValidateResponse:
    try:
        trigger_ingestion(db, audit)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.refresh(audit)
    return ValidateResponse(
        audit_id=audit.id,
        status=AuditStatus(audit.status),
        message="Validation started.",
    )


@router.get("/audit/{audit_id}/validation", response_model=ValidationReportResponse)
def get_validation_report(
    audit: Audit = Depends(verify_audit_session),
) -> ValidationReportResponse:
    data = get_validation_response(audit)
    platform = None
    if data.get("platform"):
        try:
            from core.enums import Platform

            platform = Platform(data["platform"])
        except ValueError:
            platform = None

    validation_result = None
    if data.get("validation_result"):
        try:
            validation_result = ValidationResult(data["validation_result"])
        except ValueError:
            validation_result = None

    return ValidationReportResponse(
        audit_id=audit.id,
        status=AuditStatus(audit.status),
        platform=platform,
        column_mappings=data.get("column_mappings", {}),
        validation_result=validation_result,
        validation_report=data.get("validation_report", {}),
        ingestion_error=data.get("ingestion_error"),
        can_proceed_to_scan=data.get("can_proceed_to_scan", False),
        summary=data.get("summary", {}),
    )


@router.post(
    "/audit/{audit_id}/scan",
    response_model=ScanResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_scan(
    audit: Audit = Depends(verify_audit_session),
    db: Session = Depends(get_db),
) -> ScanResponse:
    try:
        trigger_verification(db, audit)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.refresh(audit)
    return ScanResponse(
        audit_id=audit.id,
        status=AuditStatus(audit.status),
        message="Verification scan started.",
    )


@router.get("/audit/{audit_id}/scan", response_model=ScanReportResponse)
def get_scan_report(
    audit: Audit = Depends(verify_audit_session),
) -> ScanReportResponse:
    data = get_scan_response(audit)
    return ScanReportResponse(
        audit_id=audit.id,
        status=AuditStatus(data["status"]),
        scan_report=data.get("scan_report", {}),
        scan_error=data.get("scan_error"),
        finding_count=data.get("finding_count", 0),
        recoverable_arr=data.get("recoverable_arr", "0"),
        rules_completed=data.get("rules_completed", 0),
        rules_total=data.get("rules_total", 0),
        overall_confidence=data.get("overall_confidence"),
    )
