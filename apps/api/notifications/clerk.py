import logging
from dataclasses import dataclass

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClerkUserInfo:
    email: str | None
    public_metadata: dict


def _extract_primary_email(data: dict) -> str | None:
    primary = data.get("primary_email_address_id")
    for entry in data.get("email_addresses", []):
        if entry.get("id") == primary:
            return entry.get("email_address")
    if data.get("email_addresses"):
        return data["email_addresses"][0].get("email_address")
    return None


def fetch_clerk_user(clerk_user_id: str) -> ClerkUserInfo | None:
    if not settings.clerk_secret_key:
        return None
    try:
        response = httpx.get(
            f"https://api.clerk.com/v1/users/{clerk_user_id}",
            headers={"Authorization": f"Bearer {settings.clerk_secret_key}"},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        metadata = data.get("public_metadata")
        return ClerkUserInfo(
            email=_extract_primary_email(data),
            public_metadata=metadata if isinstance(metadata, dict) else {},
        )
    except Exception:
        logger.exception("Failed to fetch Clerk user for %s", clerk_user_id)
    return None


def fetch_clerk_user_email(clerk_user_id: str) -> str | None:
    user = fetch_clerk_user(clerk_user_id)
    return user.email if user else None
