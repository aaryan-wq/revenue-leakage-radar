import uuid

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from audit.service import get_audit_by_id, link_audit_to_user
from auth.dependencies import get_optional_clerk_user_id, verify_audit_session
from database.session import get_db
from models import Audit, Finding, Report
from reports.service import get_report_by_id


def _not_found(detail: str = "Not found.") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def link_audit_explicitly(
    audit: Audit,
    clerk_user_id: str,
    db: Session,
) -> Audit:
    if audit.clerk_user_id and audit.clerk_user_id != clerk_user_id:
        raise _not_found()
    if audit.clerk_user_id == clerk_user_id:
        return audit
    return link_audit_to_user(db, audit, clerk_user_id)


def _grant_report_access(
    audit: Audit,
    *,
    clerk_user_id: str | None,
    x_audit_session: str | None,
) -> bool:
    if audit.clerk_user_id:
        return bool(clerk_user_id and audit.clerk_user_id == clerk_user_id)
    return bool(x_audit_session and audit.session_token == x_audit_session)


async def verify_report_access(
    report_id: uuid.UUID,
    x_audit_session: str | None = Header(default=None, alias="X-Audit-Session"),
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
) -> Report:
    report = get_report_by_id(db, report_id)
    if not report:
        raise _not_found("Report not found.")

    audit = get_audit_by_id(db, report.audit_id)
    if not audit:
        raise _not_found("Report not found.")

    if not _grant_report_access(audit, clerk_user_id=clerk_user_id, x_audit_session=x_audit_session):
        raise _not_found("Report not found.")

    return report


async def verify_report_purchased(
    report_id: uuid.UUID,
    x_audit_session: str | None = Header(default=None, alias="X-Audit-Session"),
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
) -> Report:
    report = await verify_report_access(report_id, x_audit_session, db, clerk_user_id)

    if not report.purchased:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Report has not been purchased.",
        )

    return report


async def verify_finding_access(
    finding_id: uuid.UUID,
    x_audit_session: str | None = Header(default=None, alias="X-Audit-Session"),
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
) -> Finding:
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise _not_found("Finding not found.")

    report = db.query(Report).filter(Report.audit_id == finding.audit_id).first()
    if not report:
        raise _not_found("Finding not found.")

    await verify_report_purchased(report.id, x_audit_session, db, clerk_user_id)
    return finding


async def verify_summary_access(
    audit_id: uuid.UUID,
    x_audit_session: str | None = Header(default=None, alias="X-Audit-Session"),
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
) -> Audit:
    return await verify_audit_session(audit_id, x_audit_session, db, clerk_user_id)
