import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from models import Audit, Report
from payments.entitlements import get_reports_remaining


def upsert_report(
    db: Session,
    audit_id: uuid.UUID,
    recoverable_arr: Decimal,
    finding_count: int,
    confidence: Decimal | None,
) -> Report:
    report = db.query(Report).filter(Report.audit_id == audit_id).first()
    if report:
        report.recoverable_arr = recoverable_arr
        report.finding_count = finding_count
        report.confidence = confidence
        report.generated_at = datetime.now(timezone.utc)
    else:
        report = Report(
            audit_id=audit_id,
            recoverable_arr=recoverable_arr,
            finding_count=finding_count,
            confidence=confidence,
            purchased=False,
            generated_at=datetime.now(timezone.utc),
        )
        db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_report_by_id(db: Session, report_id: uuid.UUID) -> Report | None:
    return db.query(Report).filter(Report.id == report_id).first()


def get_report_by_audit_id(db: Session, audit_id: uuid.UUID) -> Report | None:
    return db.query(Report).filter(Report.audit_id == audit_id).first()


def unlock_report(db: Session, report: Report, *, checkout_type: str = "single_report") -> Report:
    from analytics import audit_summary, tracking

    report.purchased = True
    audit = db.query(Audit).filter(Audit.id == report.audit_id).first()
    if audit is not None:
        audit_summary.mark_report_unlocked(db, audit)
        tracking.track_report_unlocked(audit, checkout_type=checkout_type)
    db.commit()
    db.refresh(report)
    return report


def list_user_reports(db: Session, clerk_user_id: str) -> list[dict]:
    audits = (
        db.query(Audit)
        .options(joinedload(Audit.report), joinedload(Audit.company))
        .filter(Audit.clerk_user_id == clerk_user_id)
        .order_by(Audit.created_at.desc())
        .all()
    )

    items: list[dict] = []
    for audit in audits:
        report = audit.report
        if not report:
            continue
        items.append(
            {
                "audit_id": str(audit.id),
                "report_id": str(report.id),
                "date": audit.created_at.isoformat() if audit.created_at else None,
                "recoverable_arr": str(report.recoverable_arr),
                "status": audit.status,
                "finding_count": report.finding_count,
                "purchased": report.purchased,
                "company_name": audit.company.name if audit.company else None,
            }
        )
    return items


def build_dashboard(db: Session, clerk_user_id: str) -> dict:
    audits = list_user_reports(db, clerk_user_id)
    company_name = audits[0]["company_name"] if audits else None
    return {
        "company_name": company_name,
        "reports_remaining": get_reports_remaining(db, clerk_user_id),
        "audits": audits,
    }
