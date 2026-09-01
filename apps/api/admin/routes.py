import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from admin.schemas import (
    AdminAssessmentDetailResponse,
    AdminAuditDetailResponse,
    AdminMeResponse,
    AdminOverviewResponse,
    AdminRefundRequest,
    AdminRefundResponse,
    AdminReprocessRequest,
    AdminReprocessResponse,
    PaginatedAccountsResponse,
    PaginatedAssessmentsResponse,
    PaginatedAuditsResponse,
    PaginatedCompaniesResponse,
    PaginatedLogsResponse,
    PaginatedReportsResponse,
    PaginatedSupportNotesResponse,
    SupportNoteCreateRequest,
    SupportNoteResponse,
)
from admin.service import (
    admin_delete_report,
    admin_delete_upload,
    admin_reprocess_audit,
    admin_refund_purchase,
    admin_unlock_report,
    build_admin_overview,
    build_operational_logs,
    create_support_note,
    get_admin_assessment_detail,
    get_admin_audit_detail,
    list_admin_accounts,
    list_admin_assessments,
    list_admin_audits,
    list_admin_reports,
    list_support_notes,
    search_companies,
)
from auth.admin import AdminContext, require_admin
from database.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/me", response_model=AdminMeResponse)
def admin_me(admin: AdminContext = Depends(require_admin)) -> AdminMeResponse:
    return AdminMeResponse(is_admin=True, email=admin.email)


@router.get("/overview", response_model=AdminOverviewResponse)
def admin_overview(
    db: Session = Depends(get_db),
    _admin: AdminContext = Depends(require_admin),
) -> AdminOverviewResponse:
    return AdminOverviewResponse(**build_admin_overview(db))


@router.get("/companies", response_model=PaginatedCompaniesResponse)
def admin_companies(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: AdminContext = Depends(require_admin),
) -> PaginatedCompaniesResponse:
    return PaginatedCompaniesResponse(**search_companies(db, q=q, page=page, page_size=page_size))


@router.get("/accounts", response_model=PaginatedAccountsResponse)
def admin_accounts(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: AdminContext = Depends(require_admin),
) -> PaginatedAccountsResponse:
    return PaginatedAccountsResponse(**list_admin_accounts(db, q=q, page=page, page_size=page_size))


@router.get("/audits", response_model=PaginatedAuditsResponse)
def admin_audits(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: AdminContext = Depends(require_admin),
) -> PaginatedAuditsResponse:
    return PaginatedAuditsResponse(**list_admin_audits(db, q=q, page=page, page_size=page_size))


@router.get("/audits/{audit_id}", response_model=AdminAuditDetailResponse)
def admin_audit_detail(
    audit_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: AdminContext = Depends(require_admin),
) -> AdminAuditDetailResponse:
    detail = get_admin_audit_detail(db, audit_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found.")
    return AdminAuditDetailResponse(**detail)


@router.get("/reports", response_model=PaginatedReportsResponse)
def admin_reports(
    q: str | None = Query(default=None),
    purchased: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: AdminContext = Depends(require_admin),
) -> PaginatedReportsResponse:
    return PaginatedReportsResponse(
        **list_admin_reports(db, q=q, purchased=purchased, page=page, page_size=page_size)
    )


@router.get("/assessments", response_model=PaginatedAssessmentsResponse)
def admin_assessments(
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: AdminContext = Depends(require_admin),
) -> PaginatedAssessmentsResponse:
    return PaginatedAssessmentsResponse(
        **list_admin_assessments(db, q=q, status=status, page=page, page_size=page_size)
    )


@router.get("/assessments/{assessment_id}", response_model=AdminAssessmentDetailResponse)
def admin_assessment_detail(
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: AdminContext = Depends(require_admin),
) -> AdminAssessmentDetailResponse:
    detail = get_admin_assessment_detail(db, assessment_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return AdminAssessmentDetailResponse(**detail)


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_report_route(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: AdminContext = Depends(require_admin),
) -> None:
    try:
        admin_delete_report(db, report_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    create_support_note(
        db,
        entity_type="report",
        entity_id=str(report_id),
        author_clerk_user_id=admin.clerk_user_id,
        body=f"Report {report_id} deleted by admin.",
    )
    logger.info("Admin %s deleted report %s", admin.clerk_user_id, report_id)


@router.post("/reports/{report_id}/unlock")
def admin_unlock_report_route(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: AdminContext = Depends(require_admin),
) -> dict:
    try:
        report = admin_unlock_report(db, report_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    create_support_note(
        db,
        entity_type="report",
        entity_id=str(report_id),
        author_clerk_user_id=admin.clerk_user_id,
        body=f"Report {report_id} unlocked by admin.",
    )
    return {"report_id": str(report.id), "purchased": report.purchased}


@router.delete("/uploads/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_upload_route(
    upload_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: AdminContext = Depends(require_admin),
) -> None:
    try:
        admin_delete_upload(db, upload_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    create_support_note(
        db,
        entity_type="upload",
        entity_id=str(upload_id),
        author_clerk_user_id=admin.clerk_user_id,
        body=f"Upload {upload_id} deleted by admin.",
    )
    logger.info("Admin %s deleted upload %s", admin.clerk_user_id, upload_id)


@router.post("/reprocess", response_model=AdminReprocessResponse)
def admin_reprocess_route(
    body: AdminReprocessRequest,
    db: Session = Depends(get_db),
    admin: AdminContext = Depends(require_admin),
) -> AdminReprocessResponse:
    try:
        result = admin_reprocess_audit(db, body.audit_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    create_support_note(
        db,
        entity_type="audit",
        entity_id=str(body.audit_id),
        author_clerk_user_id=admin.clerk_user_id,
        body=f"Audit {body.audit_id} reprocess triggered by admin.",
    )
    return AdminReprocessResponse(**result)


@router.get("/logs", response_model=PaginatedLogsResponse)
def admin_logs(
    entity_type: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _admin: AdminContext = Depends(require_admin),
) -> PaginatedLogsResponse:
    return PaginatedLogsResponse(
        **build_operational_logs(
            db,
            entity_type=entity_type,
            entity_id=entity_id,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/refunds", response_model=AdminRefundResponse)
def admin_refund_route(
    body: AdminRefundRequest,
    db: Session = Depends(get_db),
    admin: AdminContext = Depends(require_admin),
) -> AdminRefundResponse:
    try:
        result = admin_refund_purchase(
            db,
            purchase_id=body.purchase_id,
            reason=body.reason,
            admin_user_id=admin.clerk_user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Admin refund failed for purchase %s", body.purchase_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Refund could not be processed.",
        ) from exc

    return AdminRefundResponse(**result)


@router.get("/support-notes", response_model=PaginatedSupportNotesResponse)
def admin_support_notes_list(
    entity_type: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: AdminContext = Depends(require_admin),
) -> PaginatedSupportNotesResponse:
    data = list_support_notes(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        page=page,
        page_size=page_size,
    )
    return PaginatedSupportNotesResponse(
        items=[SupportNoteResponse.model_validate(note) for note in data["items"]],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
    )


@router.post("/support-notes", response_model=SupportNoteResponse, status_code=status.HTTP_201_CREATED)
def admin_support_notes_create(
    body: SupportNoteCreateRequest,
    db: Session = Depends(get_db),
    admin: AdminContext = Depends(require_admin),
) -> SupportNoteResponse:
    note = create_support_note(
        db,
        entity_type=body.entity_type,
        entity_id=body.entity_id,
        author_clerk_user_id=admin.clerk_user_id,
        body=body.body,
    )
    return SupportNoteResponse.model_validate(note)
