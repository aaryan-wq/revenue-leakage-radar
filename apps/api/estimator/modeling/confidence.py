from typing import Any


def compute_confidence(normalized: dict[str, Any], complexity: dict[str, int], answers: dict[str, Any]) -> str:
    score = 0
    if normalized.get("arr_usd", 0) > 0:
        score += 1
    if answers.get("profile.customer_count"):
        score += 1
    unknown_count = sum(1 for v in answers.values() if v == "unknown")
    if unknown_count <= 2:
        score += 1
    if complexity["total"] <= 28:
        score += 1
    if score >= 3:
        return "Moderate"
    if score == 2:
        return "Low"
    return "Low"


def confidence_decomposition() -> dict[str, str]:
    return {
        "input_completeness": "HIGH",
        "cross_answer_consistency": "HIGH",
        "model_stability": "MEDIUM",
        "empirical_calibration": "LOW",
    }
