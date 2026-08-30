"""Model governance helpers for estimator versioning."""

from datetime import datetime, timezone

GOVERNANCE_LOG: list[dict[str, str]] = [
    {
        "model_version": "1.0.0",
        "reason_for_change": "Initial structural model release",
        "prior_version": "",
        "status": "production",
        "deployed_at": datetime.now(timezone.utc).isoformat(),
    }
]


def list_governance_records() -> list[dict[str, str]]:
    return list(GOVERNANCE_LOG)


def append_governance_record(
    version: str,
    reason: str,
    prior_version: str | None = None,
) -> dict[str, str]:
    record = {
        "model_version": version,
        "reason_for_change": reason,
        "prior_version": prior_version or "",
        "status": "production",
        "deployed_at": datetime.now(timezone.utc).isoformat(),
    }
    GOVERNANCE_LOG.append(record)
    return record
