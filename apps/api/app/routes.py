import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from audit.service import (
    abandon_audit_session,
    create_audit,
    delete_user_audit,
    get_audit_by_id,
    get_audit_data_tier_for_audit,
    get_available_entities_for_audit,
    get_coverage_analysis_for_audit,
    get_missing_recommended_file_types,
    get_missing_entities_for_audit,
    get_missing_required_file_types,
    get_scan_response_with_recovery,
    get_validation_response,
    has_billing_upload,
    recover_stale_ingestion_if_needed,
    trigger_ingestion,
    trigger_verification,
)
from auth.dependencies import require_clerk_user_id, verify_audit_session, verify_audit_write_session
from auth.report_access import link_audit_explicitly
from core.data_tiers import tier_0_complete
from core.enums import AuditStatus, DataTier, FileType, UploadStatus, ValidationResult
from database.session import get_db
from models import Audit
from schemas import (
    AuditCreateResponse,
    AuditStatusResponse,
    CoverageAnalysis,
    ScanReportResponse,
    ScanResponse,
    UploadResponse,
    ValidateResponse,
    ValidationReportResponse,
)
from upload.service import delete_upload as remove_upload, maybe_auto_trigger_ingestion, save_upload

logger = logging.getLogger(__name__)

router = APIRouter(tags=["audit"])
MAX_FILES_PER_UPLOAD = 20


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


def _can_proceed_to_scan(audit: Audit) -> bool:
    return audit.validation_result in (
        ValidationResult.READY.value,
        ValidationResult.WARNINGS.value,
    ) and audit.status in (
        AuditStatus.READY_FOR_SCAN.value,
        AuditStatus.PROCESSING_FAILED.value,
    )


@router.post("/audit", response_model=AuditCreateResponse, status_code=status.HTTP_201_CREATED)
def create_audit_session(db: Session = Depends(get_db)) -> AuditCreateResponse:
    from analytics.tracking import track_audit_created

    audit = create_audit(db)
    track_audit_created(audit)
    logger.info("Created audit session %s", audit.id)
    return AuditCreateResponse(
        audit_id=audit.id,
        session_token=audit.session_token,
        status=AuditStatus(audit.status),
    )


@router.post("/audit/{audit_id}/link", status_code=status.HTTP_204_NO_CONTENT)
def link_audit_account(
    audit: Audit = Depends(verify_audit_write_session),
    clerk_user_id: str = Depends(require_clerk_user_id),
    db: Session = Depends(get_db),
) -> None:
    try:
        link_audit_explicitly(audit, clerk_user_id, db)
    except HTTPException:
        raise
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found.") from exc


@router.get("/audit/{audit_id}", response_model=AuditStatusResponse)
def get_audit_status(
    audit: Audit = Depends(verify_audit_session),
) -> AuditStatusResponse:
    missing = get_missing_required_file_types(audit)
    recommended_missing = get_missing_recommended_file_types(audit)
    available_entities = sorted(get_available_entities_for_audit(audit), key=lambda entity: entity.value)
    missing_entities = get_missing_entities_for_audit(audit)
    data_tier = get_audit_data_tier_for_audit(audit)
    billing_upload = has_billing_upload(audit)
    coverage_raw = get_coverage_analysis_for_audit(audit) if billing_upload else None
    coverage = CoverageAnalysis(**coverage_raw) if coverage_raw else None
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
        required_files_present=billing_upload,
        has_billing_upload=billing_upload,
        tier_0_complete=tier_0_complete({FileType(u.file_type) for u in audit.uploads if u.status in ("uploaded", "purged")}),
        missing_file_types=missing,
        missing_recommended_file_types=recommended_missing,
        available_entities=available_entities,
        missing_entities=missing_entities,
        data_tier=data_tier,
        coverage_analysis=coverage,
        platform=audit.platform,
        validation_result=validation_result,
        can_proceed_to_scan=_can_proceed_to_scan(audit),
        ingestion_error=audit.ingestion_error,
    )


@router.delete("/audit/{audit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_audit(
    audit_id: UUID,
    clerk_user_id: str = Depends(require_clerk_user_id),
    db: Session = Depends(get_db),
) -> None:
    audit = get_audit_by_id(db, audit_id)
    if not audit or audit.clerk_user_id != clerk_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found.")
    try:
        delete_user_audit(db, audit, clerk_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    logger.info("Audit %s deleted by user %s", audit_id, clerk_user_id)


@router.delete("/audit/{audit_id}/session", status_code=status.HTTP_204_NO_CONTENT)
def discard_audit_session(
    audit: Audit = Depends(verify_audit_write_session),
    db: Session = Depends(get_db),
) -> None:
    """Discard an in-progress audit when the user exits before completion."""
    try:
        abandon_audit_session(db, audit)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/audit/{audit_id}/upload",
    response_model=list[UploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_files(
    files: list[UploadFile] = File(...),
    audit: Audit = Depends(verify_audit_write_session),
    db: Session = Depends(get_db),
) -> list[UploadResponse]:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required.",
        )
    if len(files) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_FILES_PER_UPLOAD} files per upload request.",
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


@router.delete(
    "/audit/{audit_id}/upload/{upload_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_upload_file(
    upload_id: UUID,
    audit: Audit = Depends(verify_audit_write_session),
    db: Session = Depends(get_db),
) -> None:
    try:
        remove_upload(db, audit, upload_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    logger.info("Removed upload %s from audit %s", upload_id, audit.id)


@router.post(
    "/audit/{audit_id}/validate",
    response_model=ValidateResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_validation(
    audit: Audit = Depends(verify_audit_write_session),
    db: Session = Depends(get_db),
) -> ValidateResponse:
    recover_stale_ingestion_if_needed(db, audit)
    db.refresh(audit)
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
    db: Session = Depends(get_db),
) -> ValidationReportResponse:
    recover_stale_ingestion_if_needed(db, audit)
    db.refresh(audit)
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
    audit: Audit = Depends(verify_audit_write_session),
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
    db: Session = Depends(get_db),
) -> ScanReportResponse:
    data = get_scan_response_with_recovery(db, audit)
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
