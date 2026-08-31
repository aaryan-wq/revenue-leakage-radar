from typing import Any

from estimator.modeling.format import round_display_amount


def complexity_tier(label: str) -> str:
    normalized = (label or "").lower().replace(" ", "_")
    if "very" in normalized and "high" in normalized:
        return "very_high"
    if "high" in normalized:
        return "high"
    if "moderate" in normalized or "medium" in normalized:
        return "moderate"
    return "low"


def compute_benchmark_context(
    arr: float,
    complexity_label: str,
    model_central: float,
    priors: dict[str, Any],
) -> dict[str, Any] | None:
    floors = priors.get("benchmark_floors") or []
    if arr <= 0 or not floors:
        return None

    tier = complexity_tier(complexity_label)
    match = None
    for row in sorted(floors, key=lambda item: float(item.get("arr_min", 0)), reverse=True):
        if arr < float(row.get("arr_min", 0)):
            continue
        allowed = [str(item).lower() for item in row.get("complexity_labels", [])]
        if allowed and tier not in allowed:
            continue
        match = row
        break

    if match is None:
        return None

    pct_low = float(match.get("pct_arr_low", 0))
    pct_high = float(match.get("pct_arr_high", 0))
    low_usd = round_display_amount(arr * pct_low)
    high_usd = round_display_amount(arr * pct_high)
    model_pct = (model_central / arr) * 100 if arr > 0 else 0.0
    may_understate = model_pct < pct_low

    return {
        "source": str(match.get("source", "industry_context")),
        "pct_arr_low": pct_low,
        "pct_arr_high": pct_high,
        "low_usd": low_usd,
        "high_usd": high_usd,
        "model_pct_of_arr": round(model_pct, 2),
        "may_understate": may_understate,
    }
