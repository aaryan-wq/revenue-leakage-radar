import logging
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status

from auth.dependencies import require_clerk_user_id
from core.config import settings
from notifications.clerk import fetch_clerk_user

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AdminContext:
    clerk_user_id: str
    email: str | None


def _is_admin_email(email: str | None) -> bool:
    if not email:
        return False
    return email.strip().lower() in settings.admin_email_list


def _is_admin_metadata(public_metadata: dict | None) -> bool:
    if not public_metadata:
        return False
    return public_metadata.get("role") == "admin"


def is_admin_clerk_user(clerk_user_id: str) -> tuple[bool, str | None]:
    user = fetch_clerk_user(clerk_user_id)
    if user is None:
        logger.warning("Unable to resolve Clerk user %s for admin check", clerk_user_id)
        return False, None

    if _is_admin_metadata(user.public_metadata):
        return True, user.email
    if _is_admin_email(user.email):
        return True, user.email
    return False, user.email


async def require_admin(
    clerk_user_id: str = Depends(require_clerk_user_id),
) -> AdminContext:
    is_admin, email = is_admin_clerk_user(clerk_user_id)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return AdminContext(clerk_user_id=clerk_user_id, email=email)
