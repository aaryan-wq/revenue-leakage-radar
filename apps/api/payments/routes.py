import logging
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from audit.service import get_audit_by_id
from auth.dependencies import require_clerk_user_id
from core.enums import CheckoutPlan
from database.session import get_db
from payments.entitlements import can_unlock_with_credit, consume_credit_and_unlock
from payments.service import (
    FulfillmentError,
    build_billing_summary,
    create_checkout_session,
    ensure_stripe_configured,
    get_checkout_status,
    handle_stripe_webhook,
)
from reports.service import get_report_by_id

logger = logging.getLogger(__name__)

router = APIRouter(tags=["payments"])


class CheckoutRequest(BaseModel):
    plan: CheckoutPlan
    report_id: uuid.UUID | None = None


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class CheckoutStatusResponse(BaseModel):
    session_id: str
    payment_status: str
    report_id: str | None = None
    plan: str | None = None
    fulfilled: bool
    reports_remaining: int


class PurchaseRecordResponse(BaseModel):
    report_id: str | None
    plan: str
    amount_cents: int | None = None
    currency: str | None = None
    receipt_url: str | None = None
    created_at: str | None = None


class BillingResponse(BaseModel):
    plan: str
    status: str
    reports_remaining: int
    portal_url: str | None = None
    purchases: list[PurchaseRecordResponse]


class UnlockCreditResponse(BaseModel):
    report_id: uuid.UUID
    purchased: bool
    reports_remaining: int
    message: str


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    body: CheckoutRequest,
    clerk_user_id: str = Depends(require_clerk_user_id),
    x_audit_session: str | None = Header(default=None, alias="X-Audit-Session"),
    db: Session = Depends(get_db),
) -> CheckoutResponse:
    try:
        ensure_stripe_configured()
        result = create_checkout_session(
            db,
            clerk_user_id,
            body.plan,
            body.report_id,
            audit_session_token=x_audit_session,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Checkout session creation failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to start checkout. Please try again.",
        ) from exc
    return CheckoutResponse(**result)


@router.get("/checkout/status", response_model=CheckoutStatusResponse)
def checkout_status(
    session_id: str,
    clerk_user_id: str = Depends(require_clerk_user_id),
    db: Session = Depends(get_db),
) -> CheckoutStatusResponse:
    try:
        result = get_checkout_status(db, session_id, clerk_user_id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to retrieve checkout session")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve checkout status.",
        ) from exc
    return CheckoutStatusResponse(**result)


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        handle_stripe_webhook(db, payload, signature)
    except FulfillmentError as exc:
        logger.exception("Stripe webhook fulfillment failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Stripe webhook processing failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed.",
        ) from exc
    return {"status": "ok"}


@router.get("/billing", response_model=BillingResponse)
def billing(
    clerk_user_id: str = Depends(require_clerk_user_id),
    db: Session = Depends(get_db),
) -> BillingResponse:
    data = build_billing_summary(db, clerk_user_id)
    return BillingResponse(
        plan=data["plan"],
        status=data["status"],
        reports_remaining=data["reports_remaining"],
        portal_url=data["portal_url"],
        purchases=[PurchaseRecordResponse(**p) for p in data["purchases"]],
    )


@router.post("/reports/{report_id}/unlock-credit", response_model=UnlockCreditResponse)
def unlock_with_credit(
    report_id: uuid.UUID,
    clerk_user_id: str = Depends(require_clerk_user_id),
    x_audit_session: str | None = Header(default=None, alias="X-Audit-Session"),
    db: Session = Depends(get_db),
) -> UnlockCreditResponse:
    report = get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    if report.purchased:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Report is already purchased.")
    if not can_unlock_with_credit(db, clerk_user_id):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="No report credits remaining.",
        )

    audit = get_audit_by_id(db, report.audit_id)
    if not audit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found.")

    from auth.audit_access import assert_audit_modification_access

    try:
        assert_audit_modification_access(audit, clerk_user_id, x_audit_session)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    if not audit.clerk_user_id:
        from audit.service import link_audit_to_user

        link_audit_to_user(db, audit, clerk_user_id)

    try:
        consume_credit_and_unlock(db, report, clerk_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    from payments.entitlements import get_reports_remaining

    remaining = get_reports_remaining(db, clerk_user_id)
    return UnlockCreditResponse(
        report_id=report.id,
        purchased=True,
        reports_remaining=remaining,
        message="Report unlocked using membership credit.",
    )
