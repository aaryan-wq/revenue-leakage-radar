from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from auth.admin import AdminContext, is_admin_clerk_user, require_admin
from notifications.clerk import ClerkUserInfo


@pytest.mark.parametrize(
    ("metadata", "email", "expected"),
    [
        ({"role": "admin"}, "other@example.com", True),
        ({}, "aaryan@paevo.co", True),
        ({}, "other@example.com", False),
        ({"role": "member"}, "aaryan@paevo.co", True),
    ],
)
def test_is_admin_clerk_user(metadata, email, expected):
    with patch("auth.admin.fetch_clerk_user") as mock_fetch:
        mock_fetch.return_value = ClerkUserInfo(
            email=email,
            display_name="Test User",
            public_metadata=metadata,
        )
        is_admin, resolved_email = is_admin_clerk_user("user_123")
        assert is_admin is expected
        assert resolved_email == email


def test_is_admin_clerk_user_fails_closed_when_clerk_unavailable():
    with patch("auth.admin.fetch_clerk_user", return_value=None):
        is_admin, resolved_email = is_admin_clerk_user("user_123")
        assert is_admin is False
        assert resolved_email is None


@pytest.mark.asyncio
async def test_require_admin_rejects_non_admin():
    with patch("auth.admin.is_admin_clerk_user", return_value=(False, "other@example.com")):
        with pytest.raises(HTTPException) as exc:
            await require_admin(clerk_user_id="user_123")
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_admin_allows_admin():
    with patch("auth.admin.is_admin_clerk_user", return_value=(True, "aaryan@paevo.co")):
        context = await require_admin(clerk_user_id="user_123")
        assert isinstance(context, AdminContext)
        assert context.clerk_user_id == "user_123"
        assert context.email == "aaryan@paevo.co"
