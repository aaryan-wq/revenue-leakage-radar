import logging
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Annotated

from auth.audit_access import assert_audit_modification_access
from auth.dependencies import get_optional_clerk_user_id, require_clerk_user_id
from auth.report_access import (
    verify_finding_access,
    verify_report_purchased,
    verify_summary_access,
)
from core.config import settings
from database.session import get_db
from models import Audit, Finding, Report
from reports.exports import build_evidence_csv, build_findings_csv
from reports.entity_ids import EntityIdResolver
from reports.findings import build_primary_finding_lookup, serialize_finding
from reports.generator import build_report_detail
from reports.service import build_dashboard, get_report_by_id, list_user_reports, unlock_report
from reports.summary import get_audit_summary
from schemas import (
    DashboardResponse,
    FindingDetailResponse,
    FreeSummaryResponse,
    ReportDetailResponse,
    ReportListItem,
    UnlockReportResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["reports"])


@router.get("/summary/{audit_id}", response_model=FreeSummaryResponse)
def get_free_summary(
    audit: Audit = Depends(verify_summary_access),
    db: Session = Depends(get_db),
) -> FreeSummaryResponse:
    try:
        data = get_audit_summary(db, audit.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return FreeSummaryResponse(**data)


@router.get("/reports", response_model=list[ReportListItem])
def list_reports(
    clerk_user_id: str = Depends(require_clerk_user_id),
    db: Session = Depends(get_db),
) -> list[ReportListItem]:
    items = list_user_reports(db, clerk_user_id)
    return [ReportListItem(**item) for item in items]


@router.get("/reports/{report_id}", response_model=ReportDetailResponse)
def get_report(
    report: Report = Depends(verify_report_purchased),
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
) -> ReportDetailResponse:
    from analytics.tracking import track_report_viewed

    audit = db.query(Audit).filter(Audit.id == report.audit_id).first()
    if audit is not None:
        track_report_viewed(audit, user_id=clerk_user_id)
    data = build_report_detail(db, report)
    return ReportDetailResponse(**data)


@router.get("/findings/{finding_id}", response_model=FindingDetailResponse)
def get_finding(
    finding: Finding = Depends(verify_finding_access),
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
) -> FindingDetailResponse:
    from analytics.tracking import track_finding_viewed

    audit = db.query(Audit).filter(Audit.id == finding.audit_id).first()
    if audit is not None:
        track_finding_viewed(audit, finding_id=str(finding.id), user_id=clerk_user_id)
    audit_findings = db.query(Finding).filter(Finding.audit_id == finding.audit_id).all()
    entity_resolver = EntityIdResolver.for_findings(db, [finding])
    primary_by_ref = build_primary_finding_lookup(audit_findings)
    payload = serialize_finding(
        finding,
        entity_resolver=entity_resolver,
        primary_by_ref=primary_by_ref,
    )
    payload["audit_id"] = str(finding.audit_id)
    report = db.query(Report).filter(Report.audit_id == finding.audit_id).first()
    payload["report_id"] = str(report.id) if report else ""
    return FindingDetailResponse(**payload)


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    clerk_user_id: str = Depends(require_clerk_user_id),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    data = build_dashboard(db, clerk_user_id)
    return DashboardResponse(
        company_name=data["company_name"],
        reports_remaining=data["reports_remaining"],
        audits=[ReportListItem(**item) for item in data["audits"]],
    )


@router.get("/exports/csv/{report_id}")
def export_csv(
    report: Report = Depends(verify_report_purchased),
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
) -> Response:
    from analytics.tracking import track_report_exported

    audit = db.query(Audit).filter(Audit.id == report.audit_id).first()
    if audit is not None:
        track_report_exported(audit, export_format="csv", user_id=clerk_user_id)
    content = build_findings_csv(db, report)
    filename = f"revenue-findings-{report.id}.csv"
    from reports.export_cache import serve_cached_export

    return serve_cached_export(
        str(report.id),
        filename,
        "text/csv",
        content,
    )


@router.get("/exports/evidence/{report_id}")
def export_evidence_csv(
    report: Report = Depends(verify_report_purchased),
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
) -> Response:
    from analytics.tracking import track_report_exported

    audit = db.query(Audit).filter(Audit.id == report.audit_id).first()
    if audit is not None:
        track_report_exported(audit, export_format="evidence", user_id=clerk_user_id)
    content = build_evidence_csv(db, report)
    filename = f"revenue-evidence-{report.id}.csv"
    from reports.export_cache import serve_cached_export

    return serve_cached_export(
        str(report.id),
        filename,
        "text/csv",
        content,
    )


@router.get("/exports/pdf/{report_id}")
def export_pdf(
    report: Report = Depends(verify_report_purchased),
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
) -> Response:
    from analytics.tracking import track_report_exported

    audit = db.query(Audit).filter(Audit.id == report.audit_id).first()
    if audit is not None:
        track_report_exported(audit, export_format="pdf", user_id=clerk_user_id)
    try:
        from reports.pdf import build_report_pdf

        content = build_report_pdf(db, report)
    except Exception as exc:
        logger.exception("PDF export failed for report %s", report.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF export failed.",
        ) from exc
    filename = f"revenue-report-{report.id}.pdf"
    from reports.export_cache import serve_cached_export

    return serve_cached_export(
        str(report.id),
        filename,
        "application/pdf",
        content,
    )


@router.post("/dev/reports/{report_id}/unlock", response_model=UnlockReportResponse)
def dev_unlock_report(
    report_id: uuid.UUID,
    x_audit_session: Annotated[str | None, Header(alias="X-Audit-Session")] = None,
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
    db: Session = Depends(get_db),
) -> UnlockReportResponse:
    if settings.environment == "production" or not settings.dev_unlock_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    report = get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    audit = db.query(Audit).filter(Audit.id == report.audit_id).first()
    if not audit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    if clerk_user_id:
        try:
            assert_audit_modification_access(audit, clerk_user_id, x_audit_session)
        except PermissionError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    elif not x_audit_session or audit.session_token != x_audit_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    unlock_report(db, report)
    logger.info("Dev unlock applied to report %s", report.id)
    return UnlockReportResponse(
        report_id=report.id,
        purchased=True,
        message="Report unlocked for development.",
    )
