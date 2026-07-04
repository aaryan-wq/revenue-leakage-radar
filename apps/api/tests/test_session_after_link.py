import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from auth.dependencies import verify_audit_session
from audit.service import link_audit_to_user
from models import Audit


def _make_audit(clerk_user_id: str | None = None, session_token: str = "session-abc") -> Audit:
    audit = Audit(session_token=session_token, clerk_user_id=clerk_user_id)
    audit.id = uuid.uuid4()
    return audit


@pytest.mark.asyncio
async def test_linked_audit_rejects_stale_session_token():
    audit = _make_audit(clerk_user_id="user_a", session_token="session-abc")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = audit

    with pytest.raises(HTTPException) as exc_info:
        await verify_audit_session(
            audit.id,
            x_audit_session="session-abc",
            db=db,
            clerk_user_id=None,
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_linked_audit_allows_owner():
    audit = _make_audit(clerk_user_id="user_a", session_token="session-abc")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = audit

    result = await verify_audit_session(
        audit.id,
        x_audit_session=None,
        db=db,
        clerk_user_id="user_a",
    )
    assert result.id == audit.id


@pytest.mark.asyncio
async def test_unlinked_audit_allows_valid_session():
    audit = _make_audit(clerk_user_id=None, session_token="session-abc")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = audit

    result = await verify_audit_session(
        audit.id,
        x_audit_session="session-abc",
        db=db,
        clerk_user_id=None,
    )
    assert result.id == audit.id


def test_link_audit_rotates_session_token():
    audit = _make_audit(clerk_user_id=None, session_token="old-token")
    db = MagicMock()

    def _link(db_arg, audit_arg, user_id):
        audit_arg.clerk_user_id = user_id

    with patch("analytics.audit_summary.link_user_updates", side_effect=_link):
        link_audit_to_user(db, audit, "user_a")

    assert audit.clerk_user_id == "user_a"
    assert audit.session_token != "old-token"
    db.commit.assert_called()
