import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import stripe
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from audit.service import _destroy_audit_data, get_audit_by_id, trigger_verification
from core.config import settings
from core.enums import AuditStatus, SCAN_PROCESSING_STATUSES
from models import Audit, Company, PaymentEvent, Report, ReportPurchase, SupportNote, Upload
from payments.service import ensure_stripe_configured
from reports.service import get_report_by_id, unlock_report
from upload.service import delete_upload

logger = logging.getLogger(__name__)


def build_admin_overview(db: Session) -> dict:
    now = datetime.now(UTC)
    seven_days_ago = now - timedelta(days=7)

    total_audits = db.query(func.count(Audit.id)).scalar() or 0
    linked_users = db.query(func.count(func.distinct(Audit.clerk_user_id))).filter(
        Audit.clerk_user_id.isnot(None)
    ).scalar() or 0
    total_reports = db.query(func.count(Report.id)).scalar() or 0
    purchased_reports = (
        db.query(func.count(Report.id)).filter(Report.purchased.is_(True)).scalar() or 0
    )
    total_purchases = db.query(func.count(ReportPurchase.id)).scalar() or 0
    total_arr = db.query(func.coalesce(func.sum(Report.recoverable_arr), 0)).scalar() or 0
    audits_last_7_days = (
        db.query(func.count(Audit.id)).filter(Audit.created_at >= seven_days_ago).scalar() or 0
    )
    purchases_last_7_days = (
        db.query(func.count(ReportPurchase.id))
        .filter(ReportPurchase.created_at >= seven_days_ago)
        .scalar()
        or 0
    )

    return {
        "total_audits": total_audits,
        "linked_users": linked_users,
        "total_reports": total_reports,
        "purchased_reports": purchased_reports,
        "total_purchases": total_purchases,
        "total_recoverable_arr": str(total_arr),
        "audits_last_7_days": audits_last_7_days,
        "purchases_last_7_days": purchases_last_7_days,
    }


def search_companies(db: Session, *, q: str | None, page: int, page_size: int) -> dict:
    query = db.query(Company)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(Company.name.ilike(pattern))

    total = query.count()
    companies = (
        query.order_by(Company.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for company in companies:
        audit_count = db.query(func.count(Audit.id)).filter(Audit.company_id == company.id).scalar() or 0
        items.append(
            {
                "id": company.id,
                "name": company.name,
                "audit_count": audit_count,
                "created_at": company.created_at,
            }
        )

    return {"items": items, "total": total, "page": page, "page_size": page_size}


def _serialize_audit_item(audit: Audit) -> dict:
    report = audit.report
    return {
        "audit_id": audit.id,
        "report_id": report.id if report else None,
        "company_name": audit.company.name if audit.company else None,
        "clerk_user_id": audit.clerk_user_id,
        "status": audit.status,
        "recoverable_arr": str(report.recoverable_arr) if report else None,
        "finding_count": report.finding_count if report else None,
        "purchased": report.purchased if report else False,
        "created_at": audit.created_at,
        "verification_completed_at": audit.verification_completed_at,
    }


def list_admin_audits(
    db: Session,
    *,
    q: str | None,
    page: int,
    page_size: int,
) -> dict:
    query = db.query(Audit).options(joinedload(Audit.report), joinedload(Audit.company))

    if q:
        term = q.strip()
        filters = [Audit.status.ilike(f"%{term}%"), Audit.clerk_user_id.ilike(f"%{term}%")]
        try:
            audit_uuid = uuid.UUID(term)
            filters.append(Audit.id == audit_uuid)
        except ValueError:
            pass
        query = query.outerjoin(Company).filter(
            or_(*filters, Company.name.ilike(f"%{term}%"))
        )

    total = query.count()
    audits = (
        query.order_by(Audit.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [_serialize_audit_item(audit) for audit in audits],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_admin_audit_detail(db: Session, audit_id: uuid.UUID) -> dict | None:
    audit = (
        db.query(Audit)
        .options(joinedload(Audit.report), joinedload(Audit.company), joinedload(Audit.uploads))
        .filter(Audit.id == audit_id)
        .first()
    )
    if not audit:
        return None

    report = audit.report
    purchases: list[ReportPurchase] = []
    if report:
        purchases = (
            db.query(ReportPurchase)
            .filter(ReportPurchase.report_id == report.id)
            .order_by(ReportPurchase.created_at.desc())
            .all()
        )

    return {
        "audit_id": audit.id,
        "report_id": report.id if report else None,
        "company_name": audit.company.name if audit.company else None,
        "company_id": audit.company_id,
        "clerk_user_id": audit.clerk_user_id,
        "status": audit.status,
        "platform": audit.platform,
        "recoverable_arr": str(report.recoverable_arr) if report else None,
        "finding_count": report.finding_count if report else None,
        "purchased": report.purchased if report else False,
        "ingestion_error": audit.ingestion_error,
        "scan_error": audit.scan_error,
        "created_at": audit.created_at,
        "verification_completed_at": audit.verification_completed_at,
        "uploads": [
            {
                "id": upload.id,
                "file_type": upload.file_type,
                "original_filename": upload.original_filename,
                "file_size": upload.file_size,
                "status": upload.status,
                "created_at": upload.created_at,
            }
            for upload in audit.uploads
        ],
        "purchases": [
            {
                "id": purchase.id,
                "plan": purchase.plan,
                "amount_cents": purchase.amount_cents,
                "currency": purchase.currency,
                "status": purchase.status,
                "stripe_payment_intent_id": purchase.stripe_payment_intent_id,
                "created_at": purchase.created_at,
            }
            for purchase in purchases
        ],
    }


def list_admin_reports(
    db: Session,
    *,
    q: str | None,
    purchased: bool | None,
    page: int,
    page_size: int,
) -> dict:
    query = (
        db.query(Report)
        .join(Audit, Report.audit_id == Audit.id)
        .outerjoin(Company, Audit.company_id == Company.id)
        .options(joinedload(Report.audit).joinedload(Audit.company))
    )

    if purchased is not None:
        query = query.filter(Report.purchased.is_(purchased))

    if q:
        term = q.strip()
        filters = [Audit.clerk_user_id.ilike(f"%{term}%"), Audit.status.ilike(f"%{term}%")]
        try:
            parsed = uuid.UUID(term)
            filters.extend([Report.id == parsed, Audit.id == parsed])
        except ValueError:
            pass
        query = query.filter(or_(*filters, Company.name.ilike(f"%{term}%")))

    total = query.count()
    reports = (
        query.order_by(Report.generated_at.desc().nullslast(), Report.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for report in reports:
        audit = report.audit
        items.append(
            {
                "report_id": report.id,
                "audit_id": report.audit_id,
                "company_name": audit.company.name if audit and audit.company else None,
                "clerk_user_id": audit.clerk_user_id if audit else None,
                "recoverable_arr": str(report.recoverable_arr),
                "finding_count": report.finding_count,
                "purchased": report.purchased,
                "status": audit.status if audit else "unknown",
                "generated_at": report.generated_at,
            }
        )

    return {"items": items, "total": total, "page": page, "page_size": page_size}


def build_operational_logs(
    db: Session,
    *,
    entity_type: str | None,
    entity_id: str | None,
    page: int,
    page_size: int,
) -> dict:
    entries: list[dict] = []

    payment_events = db.query(PaymentEvent).order_by(PaymentEvent.processed_at.desc()).limit(500).all()
    for event in payment_events:
        entries.append(
            {
                "id": f"payment_event:{event.id}",
                "timestamp": event.processed_at,
                "log_type": "payment_event",
                "entity_type": "payment",
                "entity_id": event.stripe_event_id,
                "message": event.event_type,
                "metadata": {"payload": event.payload},
            }
        )

    audits_with_errors = (
        db.query(Audit)
        .filter(or_(Audit.ingestion_error.isnot(None), Audit.scan_error.isnot(None)))
        .order_by(Audit.updated_at.desc())
        .limit(200)
        .all()
    )
    for audit in audits_with_errors:
        if audit.ingestion_error:
            entries.append(
                {
                    "id": f"audit_ingestion:{audit.id}",
                    "timestamp": audit.updated_at or audit.created_at,
                    "log_type": "audit_error",
                    "entity_type": "audit",
                    "entity_id": str(audit.id),
                    "message": audit.ingestion_error,
                    "metadata": {"error_kind": "ingestion"},
                }
            )
        if audit.scan_error:
            entries.append(
                {
                    "id": f"audit_scan:{audit.id}",
                    "timestamp": audit.updated_at or audit.created_at,
                    "log_type": "audit_error",
                    "entity_type": "audit",
                    "entity_id": str(audit.id),
                    "message": audit.scan_error,
                    "metadata": {"error_kind": "scan"},
                }
            )

    purchases = (
        db.query(ReportPurchase)
        .order_by(ReportPurchase.created_at.desc())
        .limit(200)
        .all()
    )
    for purchase in purchases:
        entries.append(
            {
                "id": f"purchase:{purchase.id}",
                "timestamp": purchase.created_at,
                "log_type": "purchase",
                "entity_type": "purchase",
                "entity_id": str(purchase.id),
                "message": f"{purchase.plan} purchase ({purchase.status})",
                "metadata": {
                    "clerk_user_id": purchase.clerk_user_id,
                    "report_id": str(purchase.report_id) if purchase.report_id else None,
                    "amount_cents": purchase.amount_cents,
                },
            }
        )

    if entity_type:
        entries = [entry for entry in entries if entry["entity_type"] == entity_type]
    if entity_id:
        entries = [entry for entry in entries if entry["entity_id"] == entity_id]

    entries.sort(key=lambda entry: entry["timestamp"] or datetime.min.replace(tzinfo=UTC), reverse=True)
    total = len(entries)
    start = (page - 1) * page_size
    end = start + page_size

    return {"items": entries[start:end], "total": total, "page": page, "page_size": page_size}


def admin_delete_report(db: Session, report_id: uuid.UUID) -> None:
    report = get_report_by_id(db, report_id)
    if not report:
        raise ValueError("Report not found.")

    db.delete(report)
    db.commit()
    logger.info("Admin deleted report %s", report_id)


def admin_delete_upload(db: Session, upload_id: uuid.UUID) -> None:
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise ValueError("Upload not found.")

    audit = get_audit_by_id(db, upload.audit_id)
    if not audit:
        raise ValueError("Audit not found.")

    delete_upload(db, audit, upload_id)


def admin_reprocess_audit(db: Session, audit_id: uuid.UUID) -> dict:
    audit = get_audit_by_id(db, audit_id)
    if not audit:
        raise ValueError("Audit not found.")

    try:
        status = AuditStatus(audit.status)
    except ValueError as exc:
        raise ValueError("Invalid audit status.") from exc

    if status in SCAN_PROCESSING_STATUSES:
        audit.status = AuditStatus.READY_FOR_SCAN.value
        audit.scan_error = None
        db.commit()
        db.refresh(audit)

    trigger_verification(db, audit)
    db.refresh(audit)

    return {
        "audit_id": audit.id,
        "status": audit.status,
        "message": "Verification reprocess triggered.",
    }


def admin_unlock_report(db: Session, report_id: uuid.UUID) -> Report:
    report = get_report_by_id(db, report_id)
    if not report:
        raise ValueError("Report not found.")
    return unlock_report(db, report, checkout_type="admin_unlock")


def admin_refund_purchase(
    db: Session,
    *,
    purchase_id: uuid.UUID,
    reason: str | None,
    admin_user_id: str,
) -> dict:
    purchase = db.query(ReportPurchase).filter(ReportPurchase.id == purchase_id).first()
    if not purchase:
        raise ValueError("Purchase not found.")

    if purchase.status == "refunded":
        raise ValueError("Purchase is already refunded.")

    if not purchase.stripe_payment_intent_id:
        raise ValueError("Purchase has no Stripe payment intent.")

    ensure_stripe_configured()
    stripe.api_key = settings.stripe_secret_key
    stripe.Refund.create(
        payment_intent=purchase.stripe_payment_intent_id,
        reason="requested_by_customer",
        metadata={"admin_refund_reason": reason or "", "admin_user_id": admin_user_id},
    )

    purchase.status = "refunded"
    if purchase.report_id:
        report = get_report_by_id(db, purchase.report_id)
        if report:
            report.purchased = False

    note_body = f"Refund processed for purchase {purchase_id}."
    if reason:
        note_body = f"{note_body} Reason: {reason}"

    create_support_note(
        db,
        entity_type="purchase",
        entity_id=str(purchase_id),
        author_clerk_user_id=admin_user_id,
        body=note_body,
    )

    db.commit()

    return {
        "purchase_id": purchase_id,
        "status": purchase.status,
        "message": "Refund processed successfully.",
    }


def create_support_note(
    db: Session,
    *,
    entity_type: str,
    entity_id: str,
    author_clerk_user_id: str,
    body: str,
) -> SupportNote:
    note = SupportNote(
        entity_type=entity_type,
        entity_id=entity_id,
        author_clerk_user_id=author_clerk_user_id,
        body=body,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def list_support_notes(
    db: Session,
    *,
    entity_type: str | None,
    entity_id: str | None,
    page: int,
    page_size: int,
) -> dict:
    query = db.query(SupportNote)
    if entity_type:
        query = query.filter(SupportNote.entity_type == entity_type)
    if entity_id:
        query = query.filter(SupportNote.entity_id == entity_id)

    total = query.count()
    notes = (
        query.order_by(SupportNote.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": notes,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def admin_delete_audit(db: Session, audit_id: uuid.UUID) -> None:
    audit = get_audit_by_id(db, audit_id)
    if not audit:
        raise ValueError("Audit not found.")

    try:
        status = AuditStatus(audit.status)
    except ValueError as exc:
        raise ValueError("Invalid audit status.") from exc

    from audit.service import NON_DELETABLE_STATUSES

    if status in NON_DELETABLE_STATUSES:
        raise ValueError("Cannot delete an audit while processing is in progress.")

    _destroy_audit_data(db, audit)
    db.commit()
    logger.info("Admin deleted audit %s", audit_id)
