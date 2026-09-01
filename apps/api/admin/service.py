import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import stripe
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, joinedload

from admin.user_lookup import ClerkUserSummary, resolve_clerk_users
from audit.service import _destroy_audit_data, get_audit_by_id, trigger_verification
from core.config import settings
from core.enums import AuditStatus, SCAN_PROCESSING_STATUSES
from models import Audit, Company, Membership, PaymentEvent, Report, ReportPurchase, SupportNote, Upload
from models.estimator import Assessment, AssessmentModelRun, AssessmentResult, LeadProfile
from payments.service import ensure_stripe_configured
from reports.service import get_report_by_id, unlock_report
from upload.service import delete_upload

logger = logging.getLogger(__name__)


def build_admin_overview(db: Session) -> dict:
    now = datetime.now(UTC)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    total_audits = db.query(func.count(Audit.id)).scalar() or 0
    linked_users = db.query(func.count(func.distinct(Audit.clerk_user_id))).filter(
        Audit.clerk_user_id.isnot(None)
    ).scalar() or 0
    anonymous_audits = db.query(func.count(Audit.id)).filter(Audit.is_anonymous.is_(True)).scalar() or 0
    completed_audits = (
        db.query(func.count(Audit.id)).filter(Audit.status == AuditStatus.COMPLETED.value).scalar() or 0
    )
    audits_in_progress = max(total_audits - completed_audits, 0)

    total_reports = db.query(func.count(Report.id)).scalar() or 0
    purchased_reports = (
        db.query(func.count(Report.id)).filter(Report.purchased.is_(True)).scalar() or 0
    )
    total_purchases = db.query(func.count(ReportPurchase.id)).scalar() or 0
    refunded_purchases = (
        db.query(func.count(ReportPurchase.id)).filter(ReportPurchase.status == "refunded").scalar() or 0
    )
    total_arr = db.query(func.coalesce(func.sum(Report.recoverable_arr), 0)).scalar() or 0
    avg_recoverable_arr = db.query(func.coalesce(func.avg(Report.recoverable_arr), 0)).scalar() or 0
    total_purchase_revenue_cents = (
        db.query(func.coalesce(func.sum(ReportPurchase.amount_cents), 0))
        .filter(ReportPurchase.status == "completed")
        .scalar()
        or 0
    )

    audits_last_7_days = (
        db.query(func.count(Audit.id)).filter(Audit.created_at >= seven_days_ago).scalar() or 0
    )
    audits_last_30_days = (
        db.query(func.count(Audit.id)).filter(Audit.created_at >= thirty_days_ago).scalar() or 0
    )
    purchases_last_7_days = (
        db.query(func.count(ReportPurchase.id))
        .filter(ReportPurchase.created_at >= seven_days_ago)
        .scalar()
        or 0
    )
    purchases_last_30_days = (
        db.query(func.count(ReportPurchase.id))
        .filter(ReportPurchase.created_at >= thirty_days_ago)
        .scalar()
        or 0
    )

    total_companies = db.query(func.count(Company.id)).scalar() or 0
    active_memberships = (
        db.query(func.count(Membership.id)).filter(Membership.status == "active").scalar() or 0
    )

    total_assessments = db.query(func.count(Assessment.id)).scalar() or 0
    completed_assessments = (
        db.query(func.count(Assessment.id)).filter(Assessment.status == "completed").scalar() or 0
    )
    assessments_last_7_days = (
        db.query(func.count(Assessment.id)).filter(Assessment.created_at >= seven_days_ago).scalar() or 0
    )
    assessments_last_30_days = (
        db.query(func.count(Assessment.id)).filter(Assessment.created_at >= thirty_days_ago).scalar() or 0
    )
    assessments_with_leads = (
        db.query(func.count(LeadProfile.id)).scalar() or 0
    )
    assessments_scan_intent = (
        db.query(func.count(LeadProfile.id)).filter(LeadProfile.scan_intent.is_(True)).scalar() or 0
    )
    assessments_linked_to_audits = (
        db.query(func.count(Audit.id)).filter(Audit.assessment_id.isnot(None)).scalar() or 0
    )

    purchase_conversion_pct = (
        round((purchased_reports / total_reports) * 100, 1) if total_reports else 0.0
    )
    assessment_to_audit_conversion_pct = (
        round((assessments_linked_to_audits / completed_assessments) * 100, 1)
        if completed_assessments
        else 0.0
    )

    return {
        "total_audits": total_audits,
        "linked_users": linked_users,
        "anonymous_audits": anonymous_audits,
        "completed_audits": completed_audits,
        "audits_in_progress": audits_in_progress,
        "total_reports": total_reports,
        "purchased_reports": purchased_reports,
        "total_purchases": total_purchases,
        "refunded_purchases": refunded_purchases,
        "total_recoverable_arr": str(total_arr),
        "average_recoverable_arr": str(round(Decimal(str(avg_recoverable_arr)), 2)),
        "total_purchase_revenue_cents": int(total_purchase_revenue_cents),
        "audits_last_7_days": audits_last_7_days,
        "audits_last_30_days": audits_last_30_days,
        "purchases_last_7_days": purchases_last_7_days,
        "purchases_last_30_days": purchases_last_30_days,
        "total_companies": total_companies,
        "active_memberships": active_memberships,
        "purchase_conversion_pct": purchase_conversion_pct,
        "total_assessments": total_assessments,
        "completed_assessments": completed_assessments,
        "assessments_last_7_days": assessments_last_7_days,
        "assessments_last_30_days": assessments_last_30_days,
        "assessments_with_leads": assessments_with_leads,
        "assessments_scan_intent": assessments_scan_intent,
        "assessments_linked_to_audits": assessments_linked_to_audits,
        "assessment_to_audit_conversion_pct": assessment_to_audit_conversion_pct,
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


def _user_fields(
    clerk_user_id: str | None,
    users: dict[str, ClerkUserSummary],
) -> dict[str, str | None]:
    if not clerk_user_id:
        return {"clerk_user_name": None, "clerk_user_email": None}
    summary = users.get(clerk_user_id)
    if not summary:
        return {"clerk_user_name": None, "clerk_user_email": None}
    return {
        "clerk_user_name": summary.display_name,
        "clerk_user_email": summary.email,
    }


def _serialize_audit_item(audit: Audit, users: dict[str, ClerkUserSummary]) -> dict:
    report = audit.report
    return {
        "audit_id": audit.id,
        "report_id": report.id if report else None,
        "company_name": audit.company.name if audit.company else None,
        "clerk_user_id": audit.clerk_user_id,
        **_user_fields(audit.clerk_user_id, users),
        "assessment_id": audit.assessment_id,
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

    user_ids = {audit.clerk_user_id for audit in audits if audit.clerk_user_id}
    users = resolve_clerk_users(user_ids)

    return {
        "items": [_serialize_audit_item(audit, users) for audit in audits],
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

    users = resolve_clerk_users({audit.clerk_user_id} if audit.clerk_user_id else set())
    user_info = _user_fields(audit.clerk_user_id, users)

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
        **user_info,
        "assessment_id": audit.assessment_id,
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
    user_ids = {
        report.audit.clerk_user_id
        for report in reports
        if report.audit and report.audit.clerk_user_id
    }
    users = resolve_clerk_users(user_ids)

    for report in reports:
        audit = report.audit
        items.append(
            {
                "report_id": report.id,
                "audit_id": report.audit_id,
                "company_name": audit.company.name if audit and audit.company else None,
                "clerk_user_id": audit.clerk_user_id if audit else None,
                **_user_fields(audit.clerk_user_id if audit else None, users),
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


def _assessment_estimate(result: AssessmentResult | None, model_runs: list[AssessmentModelRun]) -> str | None:
    from estimator.headline import estimator_headline_from_model_run, estimator_headline_from_result

    if result and isinstance(result.result_json, dict):
        headline = estimator_headline_from_result(result.result_json)
        if headline is not None:
            return str(headline)
    if model_runs:
        latest = max(model_runs, key=lambda run: run.created_at or datetime.min.replace(tzinfo=UTC))
        fallback = estimator_headline_from_model_run(latest)
        if fallback is not None:
            return str(fallback)
    return None


def list_admin_assessments(
    db: Session,
    *,
    q: str | None,
    status: str | None,
    page: int,
    page_size: int,
) -> dict:
    query = db.query(Assessment).options(joinedload(Assessment.lead_profile), joinedload(Assessment.result))

    if status:
        query = query.filter(Assessment.status == status)

    if q:
        term = q.strip()
        filters = [
            Assessment.status.ilike(f"%{term}%"),
            Assessment.industry.ilike(f"%{term}%"),
            Assessment.country.ilike(f"%{term}%"),
        ]
        try:
            filters.append(Assessment.id == uuid.UUID(term))
        except ValueError:
            pass
        query = query.outerjoin(LeadProfile).filter(
            or_(
                *filters,
                LeadProfile.email.ilike(f"%{term}%"),
                LeadProfile.company_name.ilike(f"%{term}%"),
            )
        )

    total = query.count()
    assessments = (
        query.order_by(Assessment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    assessment_ids = [item.id for item in assessments]
    audit_by_assessment: dict[uuid.UUID, Audit] = {}
    if assessment_ids:
        linked_audits = db.query(Audit).filter(Audit.assessment_id.in_(assessment_ids)).all()
        audit_by_assessment = {audit.assessment_id: audit for audit in linked_audits if audit.assessment_id}

    model_runs_by_assessment: dict[uuid.UUID, list[AssessmentModelRun]] = {}
    if assessment_ids:
        runs = (
            db.query(AssessmentModelRun)
            .filter(AssessmentModelRun.assessment_id.in_(assessment_ids))
            .all()
        )
        for run in runs:
            model_runs_by_assessment.setdefault(run.assessment_id, []).append(run)

    clerk_ids = {
        audit_by_assessment[a.id].clerk_user_id
        for a in assessments
        if a.id in audit_by_assessment and audit_by_assessment[a.id].clerk_user_id
    }
    users = resolve_clerk_users(clerk_ids)

    items = []
    for assessment in assessments:
        lead = assessment.lead_profile
        linked_audit = audit_by_assessment.get(assessment.id)
        clerk_user_id = linked_audit.clerk_user_id if linked_audit else None
        items.append(
            {
                "assessment_id": assessment.id,
                "status": assessment.status,
                "industry": assessment.industry,
                "country": assessment.country,
                "arr_amount": str(assessment.arr_amount) if assessment.arr_amount is not None else None,
                "arr_currency": assessment.arr_currency,
                "customer_count": assessment.customer_count,
                "estimated_leakage": _assessment_estimate(
                    assessment.result,
                    model_runs_by_assessment.get(assessment.id, []),
                ),
                "lead_email": lead.email if lead else None,
                "lead_company_name": lead.company_name if lead else None,
                "lead_role": lead.role if lead else None,
                "lead_score": lead.lead_score if lead else None,
                "scan_intent": lead.scan_intent if lead else False,
                "linked_audit_id": linked_audit.id if linked_audit else None,
                "clerk_user_id": clerk_user_id,
                **_user_fields(clerk_user_id, users),
                "started_at": assessment.started_at,
                "completed_at": assessment.completed_at,
                "created_at": assessment.created_at,
            }
        )

    return {"items": items, "total": total, "page": page, "page_size": page_size}


def list_admin_accounts(
    db: Session,
    *,
    q: str | None,
    page: int,
    page_size: int,
) -> dict:
    audit_stats = (
        db.query(
            Audit.clerk_user_id.label("clerk_user_id"),
            func.count(Audit.id).label("audit_count"),
            func.max(Audit.updated_at).label("last_audit_at"),
            func.min(Audit.created_at).label("first_audit_at"),
        )
        .filter(Audit.clerk_user_id.isnot(None))
        .group_by(Audit.clerk_user_id)
        .subquery()
    )

    purchase_stats = (
        db.query(
            ReportPurchase.clerk_user_id.label("clerk_user_id"),
            func.count(ReportPurchase.id).label("purchase_count"),
        )
        .group_by(ReportPurchase.clerk_user_id)
        .subquery()
    )

    membership_ids = db.query(Membership.clerk_user_id)
    audit_user_ids = db.query(Audit.clerk_user_id).filter(Audit.clerk_user_id.isnot(None))
    all_user_ids = membership_ids.union(audit_user_ids).subquery()

    base = (
        db.query(
            all_user_ids.c.clerk_user_id,
            Membership.plan,
            Membership.status.label("membership_status"),
            Membership.reports_remaining,
            Membership.created_at.label("joined_at"),
            audit_stats.c.audit_count,
            audit_stats.c.last_audit_at,
            audit_stats.c.first_audit_at,
            purchase_stats.c.purchase_count,
        )
        .outerjoin(Membership, Membership.clerk_user_id == all_user_ids.c.clerk_user_id)
        .outerjoin(audit_stats, audit_stats.c.clerk_user_id == all_user_ids.c.clerk_user_id)
        .outerjoin(purchase_stats, purchase_stats.c.clerk_user_id == all_user_ids.c.clerk_user_id)
    )

    order_clause = desc(func.coalesce(audit_stats.c.last_audit_at, Membership.created_at))

    if q:
        term = q.strip()
        all_rows = base.order_by(order_clause).all()
        user_ids = {row.clerk_user_id for row in all_rows}
        users = resolve_clerk_users(user_ids)
        term_lower = term.lower()
        matched = []
        for row in all_rows:
            clerk_user_id = row.clerk_user_id
            if term_lower in clerk_user_id.lower():
                matched.append(row)
                continue
            summary = users.get(clerk_user_id)
            if not summary:
                continue
            if summary.email and term_lower in summary.email.lower():
                matched.append(row)
                continue
            if summary.display_name and term_lower in summary.display_name.lower():
                matched.append(row)
        total = len(matched)
        page_rows = matched[(page - 1) * page_size : page * page_size]
    else:
        total = base.count()
        page_rows = base.order_by(order_clause).offset((page - 1) * page_size).limit(page_size).all()
        users = resolve_clerk_users({row.clerk_user_id for row in page_rows})

    if q:
        users = resolve_clerk_users({row.clerk_user_id for row in page_rows})

    items = []
    for row in page_rows:
        items.append(
            {
                "clerk_user_id": row.clerk_user_id,
                **_user_fields(row.clerk_user_id, users),
                "plan": row.plan,
                "membership_status": row.membership_status,
                "reports_remaining": row.reports_remaining,
                "audit_count": row.audit_count or 0,
                "purchase_count": row.purchase_count or 0,
                "joined_at": row.joined_at,
                "last_active_at": row.last_audit_at or row.joined_at,
            }
        )

    return {"items": items, "total": total, "page": page, "page_size": page_size}


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
