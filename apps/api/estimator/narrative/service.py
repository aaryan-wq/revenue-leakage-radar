from typing import Any

from pydantic import BaseModel, ValidationError

from ai.provider import AIProviderError, call_openai_json
from estimator.modeling.confidence import confidence_decomposition
from estimator.modeling.format import format_currency_range


NARRATIVE_SYSTEM_PROMPT = """You explain modeled revenue leakage estimates for SaaS finance leaders.
Never invent financial values. Never claim actual billing findings exist.
Only reference numbers provided in the input JSON.
Return JSON with keys: headline, summary, drivers (array of strings), caveats (array), recommended_next_step."""


def build_narrative_payload(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "arr_usd": result.get("arr_usd"),
        "estimated_range": [
            result.get("estimate", {}).get("low"),
            result.get("estimate", {}).get("high"),
        ],
        "confidence": result.get("confidence"),
        "top_hypotheses": [h["name"] for h in result.get("top_hypotheses", [])[:3]],
        "drivers": [d["label"] for d in result.get("drivers", [])[:5]],
        "complexity_label": result.get("complexity", {}).get("label"),
    }


def fallback_narrative(result: dict[str, Any], view: str = "executive") -> dict[str, Any]:
    low = result.get("estimate", {}).get("low", 0)
    high = result.get("estimate", {}).get("high", 0)
    range_label = format_currency_range(low, high)
    top = result.get("top_hypotheses", [])
    top_names = ", ".join(h["name"] for h in top[:3]) if top else "billing configuration gaps"
    confidence = result.get("confidence", "Moderate")

    if view == "technical":
        summary = (
            f"Modeled exposure of {range_label} ARR ({confidence} confidence) driven by "
            f"hypothesis-weighted Monte Carlo simulation with correlation overlap adjustment."
        )
    elif view == "finance":
        summary = (
            f"A portion of recurring revenue may remain tied to historical commercial terms. "
            f"Modeled exposure: {range_label} ARR."
        )
    else:
        summary = (
            f"Your modeled recurring-revenue exposure is approximately {range_label} ARR, "
            f"with {confidence.lower()} confidence. Primary areas: {top_names}."
        )

    return {
        "headline": f"Modeled exposure: {range_label} ARR",
        "summary": summary,
        "drivers": [d["label"] for d in result.get("drivers", [])[:3]],
        "caveats": [
            "This is a modeled estimate, not a billing finding.",
            "Actual leakage requires verification against billing records.",
            "Model maturity: Structural (Stage 0). Not empirically calibrated.",
        ],
        "recommended_next_step": "Run a free deterministic billing scan to replace assumptions with evidence.",
        "confidence_decomposition": confidence_decomposition(),
        "view": view,
    }


def generate_narrative(result: dict[str, Any], view: str = "executive") -> dict[str, Any]:
    payload = build_narrative_payload(result)
    user_prompt = f"View: {view}\nInput:\n{payload}"
    try:
        raw = call_openai_json(NARRATIVE_SYSTEM_PROMPT, user_prompt)
        validated = _validate_narrative(raw)
        validated["view"] = view
        validated["confidence_decomposition"] = confidence_decomposition()
        return validated
    except (AIProviderError, ValidationError, KeyError):
        return fallback_narrative(result, view)


def _validate_narrative(raw: dict[str, Any]) -> dict[str, Any]:
    required = ["headline", "summary", "drivers", "caveats", "recommended_next_step"]
    for key in required:
        if key not in raw:
            raise ValidationError.from_exception_data("NarrativeSchema", [])
    return {
        "headline": str(raw["headline"]),
        "summary": str(raw["summary"]),
        "drivers": [str(d) for d in raw["drivers"]],
        "caveats": [str(c) for c in raw["caveats"]],
        "recommended_next_step": str(raw["recommended_next_step"]),
    }
