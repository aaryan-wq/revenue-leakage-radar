"""Calculator headline USD (matches packages/shared getEstimatorHeadlineUsd)."""

from decimal import Decimal
from typing import Any

from models.estimator import AssessmentModelRun


def estimator_headline_from_result(result_payload: dict[str, Any] | None) -> float | None:
    if not result_payload or not isinstance(result_payload, dict):
        return None
    estimate = result_payload.get("estimate")
    if not isinstance(estimate, dict):
        return None
    high = estimate.get("high")
    if high is None:
        return None
    try:
        return float(high)
    except (TypeError, ValueError):
        return None


def estimator_headline_from_model_run(run: AssessmentModelRun) -> Decimal | None:
    """Fallback when stored result_json is missing; approximate headline from percentiles."""
    scenario = (run.scenario or "aggressive").lower()
    if scenario == "aggressive":
        return run.p90 or run.p75 or run.central_estimate
    if scenario == "central":
        return run.p75 or run.central_estimate
    if scenario == "conservative":
        return run.p50 or run.central_estimate
    return run.p90 or run.p75 or run.central_estimate
