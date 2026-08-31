from dataclasses import dataclass

from notifications.clerk import fetch_clerk_user

_USER_CACHE: dict[str, "ClerkUserSummary"] = {}


@dataclass(frozen=True)
class ClerkUserSummary:
    clerk_user_id: str
    display_name: str | None
    email: str | None


def resolve_clerk_user(clerk_user_id: str) -> ClerkUserSummary:
    cached = _USER_CACHE.get(clerk_user_id)
    if cached:
        return cached

    user = fetch_clerk_user(clerk_user_id)
    summary = ClerkUserSummary(
        clerk_user_id=clerk_user_id,
        display_name=user.display_name if user else None,
        email=user.email if user else None,
    )
    _USER_CACHE[clerk_user_id] = summary
    return summary


def resolve_clerk_users(clerk_user_ids: set[str]) -> dict[str, ClerkUserSummary]:
    resolved: dict[str, ClerkUserSummary] = {}
    for clerk_user_id in clerk_user_ids:
        if not clerk_user_id:
            continue
        resolved[clerk_user_id] = resolve_clerk_user(clerk_user_id)
    return resolved
