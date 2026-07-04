"""PostHog client wrapper with safe no-op when analytics is disabled."""

from __future__ import annotations

import logging
from typing import Any

from core.config import settings

logger = logging.getLogger(__name__)

_client: Any | None = None
_initialized = False


def _get_client() -> Any | None:
    global _client, _initialized
    if _initialized:
        return _client

    _initialized = True
    if not settings.posthog_api_key:
        logger.debug("PostHog disabled, POSTHOG_API_KEY not configured")
        return None

    try:
        import posthog

        posthog.api_key = settings.posthog_api_key
        posthog.host = settings.posthog_host
        _client = posthog
    except Exception:
        logger.exception("Failed to initialize PostHog client")
        _client = None

    return _client


def is_enabled() -> bool:
    return _get_client() is not None


def capture(
    event: str,
    *,
    distinct_id: str,
    properties: dict[str, Any] | None = None,
) -> None:
    """Capture a product analytics event. No-op when PostHog is not configured."""
    client = _get_client()
    if client is None:
        return

    try:
        client.capture(
            distinct_id=distinct_id,
            event=event,
            properties=properties or {},
        )
        client.flush()
    except Exception as exc:
        logger.warning("PostHog capture failed for event %s: %s", event, exc)


def shutdown() -> None:
    client = _get_client()
    if client is None:
        return
    try:
        client.shutdown()
    except Exception:
        logger.exception("PostHog shutdown failed")
