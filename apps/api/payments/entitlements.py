import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.enums import MembershipPlan, MembershipStatus, PurchasePlan
from models import Membership, Report, ReportPurchase


def get_membership(db: Session, clerk_user_id: str) -> Membership | None:
    return db.query(Membership).filter(Membership.clerk_user_id == clerk_user_id).first()


def get_or_create_membership(db: Session, clerk_user_id: str) -> Membership:
    membership = get_membership(db, clerk_user_id)
    if membership:
        return membership
    membership = Membership(
        clerk_user_id=clerk_user_id,
        plan=MembershipPlan.NONE.value,
        reports_remaining=0,
        status=MembershipStatus.ACTIVE.value,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def get_reports_remaining(db: Session, clerk_user_id: str) -> int:
    membership = get_membership(db, clerk_user_id)
    return membership.reports_remaining if membership else 0


def can_unlock_with_credit(db: Session, clerk_user_id: str) -> bool:
    membership = get_membership(db, clerk_user_id)
    return membership is not None and membership.reports_remaining > 0


def consume_credit_and_unlock(
    db: Session,
    report: Report,
    clerk_user_id: str,
) -> Report:
    from sqlalchemy import update

    from audit.service import get_audit_by_id
    from reports.service import unlock_report

    audit = get_audit_by_id(db, report.audit_id)
    if not audit or audit.clerk_user_id != clerk_user_id:
        raise PermissionError("Report access denied.")

    result = db.execute(
        update(Membership)
        .where(
            Membership.clerk_user_id == clerk_user_id,
            Membership.reports_remaining > 0,
        )
        .values(reports_remaining=Membership.reports_remaining - 1)
    )
    if result.rowcount == 0:
        raise ValueError("No report credits remaining.")

    unlock_report(db, report, checkout_type="credit_unlock")
    purchase = ReportPurchase(
        report_id=report.id,
        clerk_user_id=clerk_user_id,
        plan=PurchasePlan.MEMBERSHIP_CREDIT.value,
        status="completed",
    )
    db.add(purchase)
    db.commit()
    db.refresh(report)
    return report


def grant_annual_membership(
    db: Session,
    clerk_user_id: str,
    stripe_customer_id: str,
    stripe_subscription_id: str,
    report_credits: int,
) -> Membership:
    membership = get_or_create_membership(db, clerk_user_id)
    membership.plan = MembershipPlan.ANNUAL.value
    membership.reports_remaining += report_credits
    membership.stripe_customer_id = stripe_customer_id
    membership.stripe_subscription_id = stripe_subscription_id
    membership.status = MembershipStatus.ACTIVE.value
    db.commit()
    db.refresh(membership)
    return membership


def update_membership_status(
    db: Session,
    stripe_subscription_id: str,
    status,
) -> Membership | None:
    membership = (
        db.query(Membership)
        .filter(Membership.stripe_subscription_id == stripe_subscription_id)
        .first()
    )
    if not membership:
        return None
    membership.status = status.value
    if status == MembershipStatus.CANCELED:
        membership.plan = MembershipPlan.NONE.value
    db.commit()
    db.refresh(membership)
    return membership


def add_report_credits(db: Session, clerk_user_id: str, credits: int) -> Membership:
    membership = get_or_create_membership(db, clerk_user_id)
    membership.reports_remaining += credits
    db.commit()
    db.refresh(membership)
    return membership


def record_report_purchase(
    db: Session,
    report_id: uuid.UUID | None,
    clerk_user_id: str,
    plan: PurchasePlan,
    *,
    stripe_checkout_session_id: str | None = None,
    stripe_payment_intent_id: str | None = None,
    amount_cents: int | None = None,
    currency: str | None = None,
    receipt_url: str | None = None,
) -> ReportPurchase | None:
    purchase = ReportPurchase(
        report_id=report_id,
        clerk_user_id=clerk_user_id,
        plan=plan.value,
        stripe_checkout_session_id=stripe_checkout_session_id,
        stripe_payment_intent_id=stripe_payment_intent_id,
        amount_cents=amount_cents,
        currency=currency,
        receipt_url=receipt_url,
        status="completed",
    )
    db.add(purchase)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(purchase)
    return purchase
