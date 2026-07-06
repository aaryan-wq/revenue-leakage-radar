"""Regression tests for development-only report unlock."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from reports.routes import dev_unlock_report


def test_dev_unlock_allows_anonymous_audit_with_valid_session():
    report_id = uuid4()
    audit_id = uuid4()
    session_token = "test-session-token"

    report = MagicMock()
    report.id = report_id
    report.audit_id = audit_id

    audit = MagicMock()
    audit.id = audit_id
    audit.session_token = session_token
    audit.clerk_user_id = None

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = audit

    with patch("reports.routes.settings") as mock_settings, patch(
        "reports.routes.get_report_by_id", return_value=report
    ), patch("reports.routes.unlock_report") as unlock_mock:
        mock_settings.environment = "development"
        mock_settings.dev_unlock_enabled = True

        response = dev_unlock_report(
            report_id=report_id,
            x_audit_session=session_token,
            clerk_user_id=None,
            db=db,
        )

    assert response.purchased is True
    unlock_mock.assert_called_once_with(db, report)


def test_dev_unlock_rejects_missing_session_for_anonymous_audit():
    report_id = uuid4()
    audit_id = uuid4()

    report = MagicMock()
    report.id = report_id
    report.audit_id = audit_id

    audit = MagicMock()
    audit.id = audit_id
    audit.session_token = "expected-token"
    audit.clerk_user_id = None

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = audit

    with patch("reports.routes.settings") as mock_settings, patch(
        "reports.routes.get_report_by_id", return_value=report
    ):
        mock_settings.environment = "development"
        mock_settings.dev_unlock_enabled = True

        with pytest.raises(HTTPException) as exc_info:
            dev_unlock_report(
                report_id=report_id,
                x_audit_session=None,
                clerk_user_id=None,
                db=db,
            )

    assert exc_info.value.status_code == 401
