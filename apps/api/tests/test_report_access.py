import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from auth.report_access import verify_report_purchased
from models import Audit, Report
from reports.service import unlock_report


@pytest.mark.asyncio
async def test_verify_report_purchased_blocks_unpurchased():
    report_id = uuid.uuid4()
    audit_id = uuid.uuid4()

    report = Report(
        id=report_id,
        audit_id=audit_id,
        recoverable_arr=Decimal("0"),
        finding_count=0,
        purchased=False,
    )
    audit = Audit(session_token="session-token", clerk_user_id=None)
    audit.id = audit_id

    db = MagicMock()
    db.query.return_value.filter.return_value.first.side_effect = [report, audit]

    with patch("auth.report_access.get_report_by_id", return_value=report), patch(
        "auth.report_access.get_audit_by_id", return_value=audit
    ):
        with pytest.raises(HTTPException) as exc:
            await verify_report_purchased(
                report_id,
                x_audit_session="session-token",
                db=db,
                clerk_user_id=None,
            )
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_verify_report_purchased_allows_purchased():
    report_id = uuid.uuid4()
    audit_id = uuid.uuid4()

    report = Report(
        id=report_id,
        audit_id=audit_id,
        recoverable_arr=Decimal("0"),
        finding_count=0,
        purchased=True,
    )
    audit = Audit(session_token="session-token")
    audit.id = audit_id

    db = MagicMock()

    with patch("auth.report_access.get_report_by_id", return_value=report), patch(
        "auth.report_access.get_audit_by_id", return_value=audit
    ):
        result = await verify_report_purchased(
            report_id,
            x_audit_session="session-token",
            db=db,
            clerk_user_id=None,
        )
        assert result.purchased is True


def test_unlock_report_sets_purchased():
    report = Report(
        id=uuid.uuid4(),
        audit_id=uuid.uuid4(),
        recoverable_arr=Decimal("1000"),
        finding_count=1,
        purchased=False,
    )
    db = MagicMock()
    unlock_report(db, report)
    assert report.purchased is True
    db.commit.assert_called_once()
