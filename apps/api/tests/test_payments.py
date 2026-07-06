import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from core.enums import CheckoutPlan
from models import Audit, Membership, Report
from payments.entitlements import (
    can_unlock_with_credit,
    consume_credit_and_unlock,
    get_or_create_membership,
    get_reports_remaining,
    grant_annual_membership,
)
from payments.service import (
    FulfillmentError,
    fulfill_checkout_session,
    get_checkout_status,
    handle_stripe_webhook,
    is_event_processed,
    record_event,
)


def _make_report(purchased: bool = False) -> Report:
    report = Report(
        id=uuid.uuid4(),
        audit_id=uuid.uuid4(),
        recoverable_arr=Decimal("1000"),
        finding_count=1,
        purchased=purchased,
    )
    return report


def _make_audit(report: Report) -> Audit:
    audit = Audit(session_token="token-123")
    audit.id = report.audit_id
    return audit


def test_get_or_create_membership_creates_new():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    membership = get_or_create_membership(db, "user_123")
    db.add.assert_called_once()
    db.commit.assert_called_once()
    assert membership.clerk_user_id == "user_123"


def test_grant_annual_membership_adds_credits():
    db = MagicMock()
    existing = Membership(
        clerk_user_id="user_123",
        plan="none",
        reports_remaining=0,
        status="active",
    )
    db.query.return_value.filter.return_value.first.return_value = existing

    membership = grant_annual_membership(
        db,
        "user_123",
        stripe_customer_id="cus_123",
        stripe_subscription_id="sub_123",
        report_credits=12,
    )
    assert membership.reports_remaining == 12
    assert membership.plan == "annual"
    db.commit.assert_called()


def test_consume_credit_and_unlock():
    report = _make_report()
    audit = _make_audit(report)
    audit.clerk_user_id = "user_123"
    membership = Membership(
        clerk_user_id="user_123",
        plan="annual",
        reports_remaining=2,
        status="active",
    )

    db = MagicMock()

    def query_side_effect(model):
        query = MagicMock()
        if model.__name__ == "Membership":
            query.filter.return_value.first.return_value = membership
        elif model.__name__ == "Audit":
            query.filter.return_value.first.return_value = audit
        return query

    db.query.side_effect = query_side_effect
    execute_result = MagicMock()
    execute_result.rowcount = 1
    db.execute.return_value = execute_result

    with patch("reports.service.unlock_report") as unlock_mock:
        consume_credit_and_unlock(db, report, "user_123")
        unlock_mock.assert_called_once_with(db, report, checkout_type="credit_unlock")
    db.execute.assert_called_once()


def test_can_unlock_with_credit():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = Membership(
        clerk_user_id="user_123",
        plan="annual",
        reports_remaining=1,
        status="active",
    )
    assert can_unlock_with_credit(db, "user_123") is True


def test_get_reports_remaining_zero_when_no_membership():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    assert get_reports_remaining(db, "user_123") == 0


def test_fulfill_checkout_session_denies_audit_owner_mismatch():
    report = _make_report(purchased=False)
    audit = _make_audit(report)
    audit.clerk_user_id = "user_a"
    db = MagicMock()

    session = {
        "id": "cs_test_123",
        "metadata": {
            "report_id": str(report.id),
            "clerk_user_id": "user_b",
            "plan": CheckoutPlan.SINGLE_REPORT.value,
        },
    }

    with patch("payments.service.get_report_by_id", return_value=report), patch(
        "payments.service.get_audit_by_id", return_value=audit
    ), patch("payments.service._is_session_fulfilled", return_value=False), patch(
        "payments.service.unlock_report"
    ) as unlock_mock, patch("payments.service.record_report_purchase") as purchase_mock:
        with pytest.raises(FulfillmentError):
            fulfill_checkout_session(db, session)
        unlock_mock.assert_not_called()
        purchase_mock.assert_not_called()


def test_fulfill_checkout_session_single_report():
    report = _make_report(purchased=False)
    audit = _make_audit(report)
    db = MagicMock()

    session = {
        "id": "cs_test_123",
        "metadata": {
            "report_id": str(report.id),
            "clerk_user_id": "user_123",
            "plan": CheckoutPlan.SINGLE_REPORT.value,
        },
        "customer": "cus_123",
        "payment_intent": "pi_123",
        "amount_total": 9900,
        "currency": "usd",
    }

    with patch("payments.service.get_report_by_id", return_value=report), patch(
        "payments.service.get_audit_by_id", return_value=audit
    ), patch("payments.service.link_audit_to_user"), patch(
        "payments.service.transition_audit_status"
    ), patch("payments.service._is_session_fulfilled", return_value=False), patch(
        "payments.service.unlock_report"
    ) as unlock_mock, patch(
        "payments.service.record_report_purchase"
    ), patch("payments.service._resolve_receipt_url", return_value=None):
        fulfill_checkout_session(db, session)
        unlock_mock.assert_called_once_with(db, report, checkout_type="single_report")


def test_fulfill_checkout_session_single_on_purchased_report_adds_credit():
    report = _make_report(purchased=True)
    audit = _make_audit(report)
    db = MagicMock()

    session = {
        "id": "cs_test_123",
        "metadata": {
            "report_id": str(report.id),
            "clerk_user_id": "user_123",
            "plan": CheckoutPlan.SINGLE_REPORT.value,
        },
    }

    with patch("payments.service.get_report_by_id", return_value=report), patch(
        "payments.service.get_audit_by_id", return_value=audit
    ), patch("payments.service.link_audit_to_user"), patch(
        "payments.service.transition_audit_status"
    ), patch("payments.service._is_session_fulfilled", return_value=False), patch(
        "payments.service.unlock_report"
    ) as unlock_mock, patch("payments.service.add_report_credits") as credit_mock, patch(
        "payments.service.record_report_purchase"
    ) as purchase_mock, patch(
        "payments.service._resolve_receipt_url", return_value=None
    ):
        fulfill_checkout_session(db, session)
        unlock_mock.assert_not_called()
        credit_mock.assert_called_once_with(db, "user_123", 1)
        purchase_mock.assert_called_once()


def test_fulfill_checkout_session_without_report_adds_credit():
    db = MagicMock()
    session = {
        "id": "cs_test_credit",
        "metadata": {
            "clerk_user_id": "user_123",
            "plan": CheckoutPlan.SINGLE_REPORT.value,
        },
        "payment_intent": "pi_123",
        "amount_total": 9900,
        "currency": "usd",
    }

    with patch("payments.service._is_session_fulfilled", return_value=False), patch(
        "payments.service.add_report_credits"
    ) as credit_mock, patch("payments.service.record_report_purchase") as purchase_mock, patch(
        "payments.service._resolve_receipt_url", return_value=None
    ):
        fulfill_checkout_session(db, session)
        credit_mock.assert_called_once_with(db, "user_123", 1)
        purchase_mock.assert_called_once()


def test_fulfill_checkout_session_annual_on_purchased_report():
    report = _make_report(purchased=True)
    audit = _make_audit(report)
    db = MagicMock()

    session = {
        "id": "cs_test_annual",
        "metadata": {
            "report_id": str(report.id),
            "clerk_user_id": "user_123",
            "plan": CheckoutPlan.ANNUAL_MEMBERSHIP.value,
        },
        "customer": "cus_123",
        "subscription": "sub_123",
        "payment_intent": "pi_123",
        "amount_total": 49900,
        "currency": "usd",
    }

    with patch("payments.service.get_report_by_id", return_value=report), patch(
        "payments.service.get_audit_by_id", return_value=audit
    ), patch("payments.service.link_audit_to_user"), patch(
        "payments.service.transition_audit_status"
    ), patch("payments.service._is_session_fulfilled", return_value=False), patch(
        "payments.service.grant_annual_membership"
    ) as grant_mock, patch("payments.service.unlock_report") as unlock_mock, patch(
        "payments.service.record_report_purchase"
    ) as purchase_mock, patch(
        "payments.service._resolve_receipt_url", return_value=None
    ):
        fulfill_checkout_session(db, session)
        grant_mock.assert_called_once()
        unlock_mock.assert_not_called()
        purchase_mock.assert_called_once()


def test_get_checkout_status_rejects_wrong_user():
    db = MagicMock()
    session = MagicMock()
    session.id = "cs_test_123"
    session.payment_status = "paid"
    session.metadata = {
        "report_id": str(uuid.uuid4()),
        "clerk_user_id": "user_owner",
        "plan": CheckoutPlan.SINGLE_REPORT.value,
    }

    with patch("payments.service.ensure_stripe_configured"), patch(
        "payments.service._configure_stripe"
    ), patch("payments.service.stripe.checkout.Session.retrieve", return_value=session):
        with pytest.raises(PermissionError):
            get_checkout_status(db, "cs_test_123", "user_other")


def test_get_checkout_status_returns_fulfilled_when_purchase_exists():
    db = MagicMock()
    session = MagicMock()
    session.id = "cs_test_123"
    session.payment_status = "paid"
    session.metadata = {
        "report_id": str(uuid.uuid4()),
        "clerk_user_id": "user_123",
        "plan": CheckoutPlan.SINGLE_REPORT.value,
    }

    with patch("payments.service.ensure_stripe_configured"), patch(
        "payments.service._configure_stripe"
    ), patch("payments.service.stripe.checkout.Session.retrieve", return_value=session), patch(
        "payments.service._is_session_fulfilled", side_effect=[True]
    ), patch("payments.service.get_reports_remaining", return_value=11):
        result = get_checkout_status(db, "cs_test_123", "user_123")

    assert result["fulfilled"] is True
    assert result["reports_remaining"] == 11


def test_get_checkout_status_fulfills_when_paid_and_not_fulfilled():
    db = MagicMock()
    session = MagicMock()
    session.id = "cs_test_123"
    session.payment_status = "paid"
    session.metadata = {
        "report_id": str(uuid.uuid4()),
        "clerk_user_id": "user_123",
        "plan": CheckoutPlan.SINGLE_REPORT.value,
    }

    with patch("payments.service.ensure_stripe_configured"), patch(
        "payments.service._configure_stripe"
    ), patch("payments.service.stripe.checkout.Session.retrieve", return_value=session), patch(
        "payments.service._is_session_fulfilled", side_effect=[False, True]
    ), patch("payments.service._session_to_dict", return_value={"id": "cs_test_123"}), patch(
        "payments.service.fulfill_checkout_session"
    ) as fulfill_mock, patch("payments.service.get_reports_remaining", return_value=12):
        result = get_checkout_status(db, "cs_test_123", "user_123")

    fulfill_mock.assert_called_once()
    assert result["fulfilled"] is True


def test_create_checkout_session_allows_annual_on_purchased_report():
    from payments.service import create_checkout_session

    report = _make_report(purchased=True)
    audit = _make_audit(report)
    audit.clerk_user_id = "user_123"
    db = MagicMock()
    stripe_session = MagicMock()
    stripe_session.url = "https://checkout.stripe.test/session"
    stripe_session.id = "cs_test_annual"

    with patch("payments.service.ensure_stripe_configured"), patch(
        "payments.service._configure_stripe"
    ), patch(
        "payments.service.settings.stripe_price_annual_membership", "price_annual_test"
    ), patch("payments.service.get_report_by_id", return_value=report), patch(
        "payments.service.get_audit_by_id", return_value=audit
    ), patch("payments.service.link_audit_to_user"), patch(
        "payments.service.transition_audit_status"
    ), patch("payments.service.get_or_create_membership") as membership_mock, patch(
        "payments.service.stripe.checkout.Session.create", return_value=stripe_session
    ) as create_mock:
        membership_mock.return_value = Membership(
            clerk_user_id="user_123",
            plan="none",
            reports_remaining=0,
            status="active",
        )
        result = create_checkout_session(
            db,
            "user_123",
            CheckoutPlan.ANNUAL_MEMBERSHIP,
            report.id,
        )

    assert result["checkout_url"] == "https://checkout.stripe.test/session"
    create_mock.assert_called_once()


def test_create_checkout_session_without_report_id():
    from payments.service import create_checkout_session

    db = MagicMock()
    stripe_session = MagicMock()
    stripe_session.url = "https://checkout.stripe.test/session"
    stripe_session.id = "cs_test_credit"

    with patch("payments.service.ensure_stripe_configured"), patch(
        "payments.service._configure_stripe"
    ), patch("payments.service.get_or_create_membership") as membership_mock, patch(
        "payments.service.stripe.checkout.Session.create", return_value=stripe_session
    ) as create_mock:
        membership_mock.return_value = Membership(
            clerk_user_id="user_123",
            plan="none",
            reports_remaining=0,
            status="active",
        )
        result = create_checkout_session(db, "user_123", CheckoutPlan.SINGLE_REPORT)

    assert result["checkout_url"] == "https://checkout.stripe.test/session"
    create_mock.assert_called_once()
    call_kwargs = create_mock.call_args.args[0] if create_mock.call_args.args else create_mock.call_args.kwargs
    # Session.create is called with keyword args dict as only positional in our code
    session_params = create_mock.call_args.kwargs if create_mock.call_args.kwargs else create_mock.call_args[1]
    if not session_params:
        session_params = create_mock.call_args[0][0]
    assert "report_id" not in (session_params.get("metadata") or {})


def test_stripe_webhook_records_event_after_fulfillment():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    event = {
        "id": "evt_new",
        "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_test_123"}},
    }

    with patch("payments.service.settings") as settings_mock, patch(
        "payments.service.stripe.Webhook.construct_event", return_value=event
    ), patch("payments.service.fulfill_checkout_session") as fulfill_mock, patch(
        "payments.service.record_event"
    ) as record_mock:
        settings_mock.stripe_webhook_secret = "whsec_test"
        handle_stripe_webhook(db, b"{}", "sig")
        fulfill_mock.assert_called_once()
        record_mock.assert_called_once_with(db, "evt_new", "checkout.session.completed", dict(event))


def test_stripe_webhook_does_not_record_event_when_fulfillment_fails():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    event = {
        "id": "evt_fail",
        "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_test_123"}},
    }

    with patch("payments.service.settings") as settings_mock, patch(
        "payments.service.stripe.Webhook.construct_event", return_value=event
    ), patch(
        "payments.service.fulfill_checkout_session", side_effect=RuntimeError("fulfillment failed")
    ), patch("payments.service.record_event") as record_mock:
        settings_mock.stripe_webhook_secret = "whsec_test"
        with pytest.raises(RuntimeError):
            handle_stripe_webhook(db, b"{}", "sig")
        record_mock.assert_not_called()


def test_is_event_processed():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = MagicMock()
    assert is_event_processed(db, "evt_123") is True


def test_record_event():
    db = MagicMock()
    record_event(db, "evt_123", "checkout.session.completed", {"id": "evt_123"})
    db.add.assert_called_once()
    db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_stripe_webhook_idempotent():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = MagicMock()

    event = {
        "id": "evt_duplicate",
        "type": "checkout.session.completed",
        "data": {"object": {}},
    }

    with patch("payments.service.settings") as settings_mock, patch(
        "payments.service.stripe.Webhook.construct_event", return_value=event
    ), patch("payments.service.is_event_processed", return_value=True), patch(
        "payments.service.fulfill_checkout_session"
    ) as fulfill_mock, patch("payments.service.record_event") as record_mock:
        settings_mock.stripe_webhook_secret = "whsec_test"
        handle_stripe_webhook(db, b"{}", "sig")
        fulfill_mock.assert_not_called()
        record_mock.assert_not_called()


def test_fulfill_checkout_session_unlocks_report_in_db():
    import secrets
    from decimal import Decimal

    from core.enums import AuditStatus, CheckoutPlan
    from database.session import SessionLocal
    from models import Audit, Report
    from payments.service import fulfill_checkout_session

    db = SessionLocal()
    audit = Audit(
        session_token=secrets.token_urlsafe(32),
        status=AuditStatus.COMPLETED.value,
    )
    db.add(audit)
    db.flush()
    report = Report(
        audit_id=audit.id,
        recoverable_arr=Decimal("1200"),
        finding_count=2,
        purchased=False,
    )
    db.add(report)
    db.commit()

    try:
        fulfill_checkout_session(
            db,
            {
                "id": "cs_integration_test",
                "metadata": {
                    "report_id": str(report.id),
                    "clerk_user_id": "user_integration",
                    "plan": CheckoutPlan.SINGLE_REPORT.value,
                },
                "amount_total": 150000,
                "currency": "usd",
            },
        )
        db.refresh(report)
        assert report.purchased is True
    finally:
        db.delete(report)
        db.delete(audit)
        db.commit()
        db.close()
