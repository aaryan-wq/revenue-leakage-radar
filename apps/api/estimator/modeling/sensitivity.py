from typing import Any


DRIVER_LABELS = {
    "contracts.negotiated_arr_pct": "Negotiated pricing prevalence",
    "contracts.grandfathering": "Grandfathered pricing",
    "discounts.frequency": "Discount frequency",
    "changes.pricing_changes_24mo": "Pricing change frequency",
    "operations.manual_override_frequency": "Manual billing intervention",
    "pricing.usage_based": "Usage-based billing",
    "quote_to_bill.quote_automation": "Quote-to-bill automation",
    "velocity.commercial_changes_12mo": "Commercial change velocity",
}


def compute_sensitivity(
    normalized: dict[str, Any],
    posteriors: dict[str, float],
    priors: dict,
    segments: dict[str, float],
) -> list[dict[str, Any]]:
    arr = segments.get("arr", 0)
    if arr <= 0:
        return []
    drivers: list[dict[str, Any]] = []
    for key, label in DRIVER_LABELS.items():
        if key not in normalized and key.split(".")[0] + "." + key.split(".")[1] not in normalized:
            # check partial keys in answers-derived normalized
            pass
        value = normalized.get(key)
        if value is None:
            continue
        weight = _driver_weight(key, value)
        drivers.append({"key": key, "label": label, "influence": weight})

    if not drivers:
        drivers = [
            {"key": "arr", "label": "Revenue scale (ARR)", "influence": 0.9},
            {"key": "complexity", "label": "Billing complexity", "influence": 0.7},
        ]
    drivers.sort(key=lambda d: d["influence"], reverse=True)
    return drivers[:5]


def _driver_weight(key: str, value: Any) -> float:
    high_values = {
        "contracts.negotiated_arr_pct": {"51_75", "76_100"},
        "contracts.grandfathering": {"frequently", "very_frequently"},
        "discounts.frequency": {"common", "nearly_all"},
        "changes.pricing_changes_24mo": {"4_5", "6_plus"},
        "operations.manual_override_frequency": {"frequently", "very_frequently"},
        "velocity.commercial_changes_12mo": {"6_10", "10_plus"},
    }
    if value is True:
        return 0.85
    if isinstance(value, str) and value in high_values.get(key, set()):
        return 0.9
    if isinstance(value, str):
        return 0.5
    return 0.4
