import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from auth.audit_access import assert_audit_modification_access
from audit.service import link_audit_to_user
from models import Audit, Report


def _make_audit(clerk_user_id: str | None = None, session_token: str = "session-abc") -> Audit:
    audit = Audit(session_token=session_token, clerk_user_id=clerk_user_id)
    audit.id = uuid.uuid4()
    return audit


def test_assert_audit_modification_access_allows_owner():
    audit = _make_audit(clerk_user_id="user_a")
    assert_audit_modification_access(audit, "user_a")


def test_assert_audit_modification_access_allows_session_for_unlinked_audit():
    audit = _make_audit(clerk_user_id=None)
    assert_audit_modification_access(audit, "user_b", session_token="session-abc")


def test_assert_audit_modification_access_blocks_other_user():
    audit = _make_audit(clerk_user_id="user_a")
    with pytest.raises(PermissionError, match="Report access denied"):
        assert_audit_modification_access(audit, "user_b")


def test_assert_audit_modification_access_blocks_unlinked_without_session():
    audit = _make_audit(clerk_user_id=None)
    with pytest.raises(PermissionError, match="Report access denied"):
        assert_audit_modification_access(audit, "user_b")


def test_assert_audit_modification_access_blocks_wrong_session():
    audit = _make_audit(clerk_user_id=None)
    with pytest.raises(PermissionError, match="Report access denied"):
        assert_audit_modification_access(audit, "user_b", session_token="wrong-token")


def test_link_audit_to_user_rejects_overwrite():
    audit = _make_audit(clerk_user_id="user_a")
    db = MagicMock()
    with pytest.raises(PermissionError, match="already linked"):
        link_audit_to_user(db, audit, "user_b")


def test_link_audit_to_user_idempotent_for_same_user():
    audit = _make_audit(clerk_user_id="user_a")
    db = MagicMock()
    result = link_audit_to_user(db, audit, "user_a")
    assert result.clerk_user_id == "user_a"
    db.commit.assert_not_called()


def test_unlock_credit_route_blocks_idor():
    from payments.routes import unlock_with_credit

    report_id = uuid.uuid4()
    audit_id = uuid.uuid4()
    report = Report(
        id=report_id,
        audit_id=audit_id,
        recoverable_arr=Decimal("1000"),
        finding_count=1,
        purchased=False,
    )
    audit = _make_audit(clerk_user_id="user_a")

    db = MagicMock()

    with patch("payments.routes.get_report_by_id", return_value=report), patch(
        "payments.routes.get_audit_by_id", return_value=audit
    ), patch("payments.routes.can_unlock_with_credit", return_value=True):
        with pytest.raises(HTTPException) as exc:
            unlock_with_credit(
                report_id,
                clerk_user_id="user_b",
                x_audit_session=None,
                db=db,
            )
        assert exc.value.status_code == 403


def test_create_checkout_session_rejects_foreign_report():
    from core.enums import CheckoutPlan
    from payments.service import create_checkout_session

    report = Report(
        id=uuid.uuid4(),
        audit_id=uuid.uuid4(),
        recoverable_arr=Decimal("1000"),
        finding_count=1,
        purchased=False,
    )
    audit = _make_audit(clerk_user_id="user_a")

    db = MagicMock()

    with patch("payments.service.ensure_stripe_configured"), patch(
        "payments.service.get_report_by_id", return_value=report
    ), patch("payments.service.get_audit_by_id", return_value=audit):
        with pytest.raises(ValueError, match="Report access denied"):
            create_checkout_session(
                db,
                "user_b",
                CheckoutPlan.SINGLE_REPORT,
                report.id,
                audit_session_token=None,
            )
