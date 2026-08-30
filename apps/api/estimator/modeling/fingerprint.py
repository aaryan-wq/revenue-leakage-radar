from typing import Any

from estimator.questionnaire.schema import load_priors


def model_fingerprint(priors: dict[str, Any] | None = None) -> dict[str, str | int]:
    data = priors or load_priors()
    return {
        "model_version": str(data.get("version", "0")),
        "calibration_stage": int(data.get("calibration_stage", 0)),
    }


def is_stale_result(result: dict[str, Any], priors: dict[str, Any] | None = None) -> bool:
    current = model_fingerprint(priors)
    stored_stage = result.get("calibration_stage")
    if stored_stage is None:
        return True
    return (
        str(result.get("model_version", "")) != current["model_version"]
        or int(stored_stage) != current["calibration_stage"]
    )
