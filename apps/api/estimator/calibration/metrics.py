"""Calibration metrics and governance (Stage 0 scaffolding)."""

from decimal import Decimal
from typing import Sequence

from models.estimator import CalibrationObservation


def mean_absolute_error(observations: Sequence[CalibrationObservation]) -> float | None:
    errors = [float(o.absolute_error) for o in observations if o.absolute_error is not None]
    if not errors:
        return None
    return sum(errors) / len(errors)


def interval_coverage(observations: Sequence[CalibrationObservation]) -> float | None:
    flags = [o.in_interval for o in observations if o.in_interval is not None]
    if not flags:
        return None
    return sum(1 for f in flags if f) / len(flags)


def governance_record(version: str, reason: str, prior_version: str | None = None) -> dict[str, str]:
    return {
        "model_version": version,
        "reason_for_change": reason,
        "prior_version": prior_version or "",
        "status": "production",
    }
