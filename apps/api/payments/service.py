import logging
import uuid
from typing import Any

import stripe
from sqlalchemy.orm import Session

from audit.service import get_audit_by_id, link_audit_to_user, transition_audit_status
from core.config import settings
from core.enums import AuditStatus, CheckoutPlan, MembershipStatus, PurchasePlan
from models import PaymentEvent, ReportPurchase
from payments.entitlements import (
    add_report_credits,
    get_membership,
    get_or_create_membership,
    get_reports_remaining,
    grant_annual_membership,
    record_report_purchase,
    update_membership_status,
)
from reports.service import get_report_by_id, unlock_report

logger = logging.getLogger(__name__)

_PAID_STATUSES = frozenset({"paid", "no_payment_required"})


class FulfillmentError(Exception):
    """Raised when Stripe checkout fulfillment cannot complete."""


def _configure_stripe() -> None:
    stripe.api_key = settings.stripe_secret_key


def ensure_stripe_configured() -> None:
    if not settings.stripe_configured:
        raise ValueError(
            "Stripe is not configured. Set STRIPE_SECRET_KEY and STRIPE_PRICE_SINGLE_REPORT."
        )


def _session_to_dict(session: Any) -> dict[str, Any]:
    if isinstance(session, dict):
        return session
    if hasattr(session, "to_dict_recursive"):
        return session.to_dict_recursive()
    return dict(session)


def _is_session_fulfilled(db: Session, session_id: str) -> bool:
    return (
        db.query(ReportPurchase)
        .filter(ReportPurchase.stripe_checkout_session_id == session_id)
        .first()
        is not None
    )


def _resolve_receipt_url(payment_intent: Any) -> str | None:
    payment_intent_id = payment_intent if isinstance(payment_intent, str) else None
    if not payment_intent_id:
        return None
    try:
        intent = stripe.PaymentIntent.retrieve(
            payment_intent_id,
            expand=["latest_charge"],
        )
        charge = intent.latest_charge
        if charge is None:
            return None
        if isinstance(charge, str):
            charge_obj = stripe.Charge.retrieve(charge)
            return charge_obj.receipt_url
        return getattr(charge, "receipt_url", None)
    except stripe.StripeError:
        logger.warning("Unable to resolve receipt URL for payment intent %s", payment_intent_id)
        return None


def _send_purchase_confirmation(clerk_user_id: str, report_id: uuid.UUID | None) -> None:
    if report_id is None:
        return
    from notifications.clerk import fetch_clerk_user_email
    from notifications.templates import purchase_confirmation_email

    email = fetch_clerk_user_email(clerk_user_id)
    if not email:
        return
    report_url = f"{settings.web_url}/report/{report_id}"
    purchase_confirmation_email(to=email, report_url=report_url)


def create_checkout_session(
    db: Session,
    clerk_user_id: str,
    plan: CheckoutPlan,
    report_id: uuid.UUID | None = None,
    audit_session_token: str | None = None,
) -> dict[str, str]:
    ensure_stripe_configured()
    _configure_stripe()

    if plan == CheckoutPlan.ANNUAL_MEMBERSHIP and not settings.annual_membership_configured:
        raise ValueError("Annual membership is not configured.")

    metadata: dict[str, str] = {
        "clerk_user_id": clerk_user_id,
        "plan": plan.value,
    }
    audit = None

    if report_id is not None:
        report = get_report_by_id(db, report_id)
        if not report:
            raise ValueError("Report not found.")

        audit = get_audit_by_id(db, report.audit_id)
        if not audit:
            raise ValueError("Audit not found.")

        from auth.audit_access import assert_audit_modification_access

        try:
            assert_audit_modification_access(audit, clerk_user_id, audit_session_token)
        except PermissionError as exc:
            raise ValueError(str(exc)) from exc

        if not audit.clerk_user_id:
            link_audit_to_user(db, audit, clerk_user_id)
        if not report.purchased or plan == CheckoutPlan.ANNUAL_MEMBERSHIP:
            transition_audit_status(db, audit, AuditStatus.PAYMENT_PENDING)

        metadata["report_id"] = str(report_id)
        metadata["audit_id"] = str(audit.id)
        cancel_url = f"{settings.web_url}/checkout/cancel?report_id={report_id}"
        client_reference_id = str(report_id)
    else:
        cancel_url = f"{settings.web_url}/checkout/cancel"
        client_reference_id = clerk_user_id

    success_url = f"{settings.web_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}"

    membership = get_or_create_membership(db, clerk_user_id)
    customer_id = membership.stripe_customer_id

    if plan == CheckoutPlan.SINGLE_REPORT:
        session_params: dict[str, Any] = {
            "mode": "payment",
            "line_items": [{"price": settings.stripe_price_single_report, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": metadata,
            "client_reference_id": client_reference_id,
        }
    else:
        session_params = {
            "mode": "subscription",
            "line_items": [{"price": settings.stripe_price_annual_membership, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": metadata,
            "client_reference_id": client_reference_id,
            "subscription_data": {"metadata": metadata},
        }

    if customer_id:
        session_params["customer"] = customer_id
    elif plan == CheckoutPlan.SINGLE_REPORT:
        session_params["customer_creation"] = "always"

    try:
        session = stripe.checkout.Session.create(**session_params)
    except stripe.StripeError as exc:
        logger.exception("Stripe checkout session creation failed")
        from analytics.tracking import track

        if report_id is not None and audit is not None:
            from analytics import events

            track(audit, events.CHECKOUT_FAILED, {"checkout_type": plan.value, "error": str(exc)})
        raise ValueError(str(exc.user_message or exc)) from exc

    if report_id is not None and audit is not None:
        from analytics import audit_summary, tracking

        audit_summary.mark_checkout_started(db, audit)
        db.commit()
        amount_usd = None
        if plan == CheckoutPlan.SINGLE_REPORT:
            amount_usd = 2500.0
        tracking.track_checkout_started(
            audit,
            checkout_type=plan.value,
            price_usd=amount_usd,
            currency="usd",
        )

    return {"checkout_url": session.url or "", "session_id": session.id}


def get_checkout_status(
    db: Session,
    session_id: str,
    clerk_user_id: str,
) -> dict[str, Any]:
    ensure_stripe_configured()
    _configure_stripe()
    session = stripe.checkout.Session.retrieve(session_id)
    metadata = session.metadata or {}
    session_owner = metadata.get("clerk_user_id")
    if session_owner != clerk_user_id:
        raise PermissionError("Checkout session access denied.")

    payment_status = session.payment_status
    fulfilled = _is_session_fulfilled(db, session_id)

    if payment_status in _PAID_STATUSES and not fulfilled:
        try:
            fulfill_checkout_session(db, _session_to_dict(session))
        except FulfillmentError:
            logger.exception("Checkout fulfillment failed during status poll for %s", session_id)
        fulfilled = _is_session_fulfilled(db, session_id)

    return {
        "session_id": session.id,
        "payment_status": payment_status,
        "report_id": metadata.get("report_id"),
        "plan": metadata.get("plan"),
        "fulfilled": fulfilled,
        "reports_remaining": get_reports_remaining(db, clerk_user_id),
    }


def build_billing_summary(db: Session, clerk_user_id: str) -> dict[str, Any]:
    membership = get_membership(db, clerk_user_id)
    plan = membership.plan if membership else "none"
    reports_remaining = membership.reports_remaining if membership else 0
    status = membership.status if membership else "none"
    portal_url: str | None = None

    if membership and membership.stripe_customer_id and settings.stripe_configured:
        _configure_stripe()
        try:
            portal = stripe.billing_portal.Session.create(
                customer=membership.stripe_customer_id,
                return_url=f"{settings.web_url}/billing",
            )
            portal_url = portal.url
        except stripe.StripeError:
            logger.warning("Failed to create billing portal session for %s", clerk_user_id)

    purchases = (
        db.query(ReportPurchase)
        .filter(ReportPurchase.clerk_user_id == clerk_user_id)
        .order_by(ReportPurchase.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "plan": plan,
        "status": status,
        "reports_remaining": reports_remaining,
        "portal_url": portal_url,
        "purchases": [
            {
                "report_id": str(p.report_id) if p.report_id else None,
                "plan": p.plan,
                "amount_cents": p.amount_cents,
                "currency": p.currency,
                "receipt_url": p.receipt_url,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in purchases
        ],
    }


def is_event_processed(db: Session, stripe_event_id: str) -> bool:
    return (
        db.query(PaymentEvent)
        .filter(PaymentEvent.stripe_event_id == stripe_event_id)
        .first()
        is not None
    )


def record_event(db: Session, stripe_event_id: str, event_type: str, payload: dict) -> None:
    minimal_payload = {
        "id": payload.get("id"),
        "type": payload.get("type"),
        "livemode": payload.get("livemode"),
    }
    data_object = (payload.get("data") or {}).get("object") or {}
    if isinstance(data_object, dict):
        minimal_payload["object_id"] = data_object.get("id")
        minimal_payload["metadata"] = data_object.get("metadata")

    event = PaymentEvent(
        stripe_event_id=stripe_event_id,
        event_type=event_type,
        payload=minimal_payload,
    )
    db.add(event)
    db.commit()


def fulfill_checkout_session(db: Session, session: dict[str, Any]) -> None:
    session_id = session.get("id")
    metadata = session.get("metadata") or {}
    report_id_str = metadata.get("report_id")
    clerk_user_id = metadata.get("clerk_user_id")
    plan_str = metadata.get("plan")

    if not clerk_user_id or not plan_str:
        raise FulfillmentError(f"Checkout session missing metadata: {session.get('id')}")

    plan = CheckoutPlan(plan_str)
    purchase_plan = (
        PurchasePlan.SINGLE_REPORT
        if plan == CheckoutPlan.SINGLE_REPORT
        else PurchasePlan.ANNUAL_MEMBERSHIP
    )
    report = None
    report_id: uuid.UUID | None = None
    audit = None

    if report_id_str:
        report_id = uuid.UUID(report_id_str)
        report = get_report_by_id(db, report_id)
        if not report:
            raise FulfillmentError(f"Report {report_id} not found for checkout fulfillment")

        audit = get_audit_by_id(db, report.audit_id)
        if audit and audit.clerk_user_id and audit.clerk_user_id != clerk_user_id:
            raise FulfillmentError(
                f"Checkout fulfillment denied: audit {audit.id} owned by {audit.clerk_user_id}, "
                f"session for {clerk_user_id}"
            )

    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    payment_intent = session.get("payment_intent")
    amount_total = session.get("amount_total")
    currency = session.get("currency")
    receipt_url = _resolve_receipt_url(payment_intent)

    claimed = record_report_purchase(
        db,
        report_id,
        clerk_user_id,
        purchase_plan,
        stripe_checkout_session_id=session_id,
        stripe_payment_intent_id=payment_intent if isinstance(payment_intent, str) else None,
        amount_cents=amount_total,
        currency=currency,
        receipt_url=receipt_url,
    )
    if claimed is None:
        logger.info("Checkout session %s already fulfilled, skipping", session_id)
        return

    if audit:
        if not audit.clerk_user_id:
            link_audit_to_user(db, audit, clerk_user_id)
        transition_audit_status(db, audit, AuditStatus.COMPLETED)

    if plan == CheckoutPlan.SINGLE_REPORT:
        if report and not report.purchased:
            unlock_report(db, report, checkout_type="single_report")
        else:
            add_report_credits(db, clerk_user_id, 1)
        if audit is not None:
            from analytics import audit_summary, tracking

            audit_summary.mark_checkout_completed(db, audit)
            price_usd = (amount_total / 100) if amount_total else 2500.0
            tracking.track_checkout_completed(
                audit,
                checkout_type="single_report",
                price_usd=price_usd,
                currency=currency or "usd",
            )
    elif plan == CheckoutPlan.ANNUAL_MEMBERSHIP:
        if customer_id and subscription_id:
            grant_annual_membership(
                db,
                clerk_user_id,
                stripe_customer_id=str(customer_id),
                stripe_subscription_id=str(subscription_id),
                report_credits=settings.annual_membership_report_credits,
            )
        if report and not report.purchased:
            unlock_report(db, report, checkout_type="annual_membership")

    db.commit()
    logger.info(
        "Fulfilled checkout plan %s report %s",
        plan_str,
        report_id_str or "none",
    )
    _send_purchase_confirmation(clerk_user_id, report_id)


def handle_stripe_webhook(db: Session, payload: bytes, signature: str) -> None:
    if not settings.stripe_webhook_secret:
        raise ValueError("Stripe webhook secret is not configured.")

    _configure_stripe()
    event = stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)

    if is_event_processed(db, event["id"]):
        logger.info("Skipping duplicate Stripe event %s", event["id"])
        return

    if event["type"] == "checkout.session.completed":
        fulfill_checkout_session(db, event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        update_membership_status(db, sub["id"], MembershipStatus.CANCELED)
    elif event["type"] == "customer.subscription.updated":
        sub = event["data"]["object"]
        stripe_status = sub.get("status", "")
        if stripe_status == "past_due":
            update_membership_status(db, sub["id"], MembershipStatus.PAST_DUE)
        elif stripe_status == "active":
            update_membership_status(db, sub["id"], MembershipStatus.ACTIVE)

    record_event(db, event["id"], event["type"], dict(event))
