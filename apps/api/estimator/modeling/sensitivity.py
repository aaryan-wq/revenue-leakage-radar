from __future__ import annotations

from typing import Any

PERTURBATIONS: dict[str, tuple[str, Any]] = {
    "contracts.grandfathering": ("contracts.grandfathering", "very_frequently"),
    "discounts.frequency": ("discounts.frequency", "nearly_all"),
    "discounts.expiry_handling": ("discounts.expiry_handling", "manual_sales"),
    "discounts.auto_expiry_removal": ("discounts.auto_expiry_removal", "never"),
    "operations.manual_override_frequency": ("operations.manual_override_frequency", "very_frequently"),
    "operations.unticketed_adjustments": ("operations.unticketed_adjustments", "very_often"),
    "quote_to_bill.quote_automation": ("quote_to_bill.quote_automation", "manual"),
    "quote_to_bill.finance_sales_disagreement": ("quote_to_bill.finance_sales_disagreement", "very_often"),
    "operations.churn_billing_cutoff": ("operations.churn_billing_cutoff", "manual"),
    "discounts.stacking_policy": ("discounts.stacking_policy", "allowed"),
    "operations.credit_memo_process": ("operations.credit_memo_process", "ad_hoc"),
    "controls.invoice_price_qa": ("controls.invoice_price_qa", "never"),
    "controls.billing_qa": ("controls.billing_qa", "never"),
    "controls.monthly_reconciliation": ("controls.monthly_reconciliation", "never"),
}

DRIVER_LABELS = {
    "contracts.grandfathering": "Grandfathered pricing",
    "discounts.frequency": "Discount frequency",
    "discounts.expiry_handling": "Discount expiry handling",
    "discounts.auto_expiry_removal": "Automatic discount removal",
    "operations.manual_override_frequency": "Manual billing intervention",
    "operations.unticketed_adjustments": "Unticketed billing adjustments",
    "quote_to_bill.quote_automation": "Quote-to-bill automation",
    "quote_to_bill.finance_sales_disagreement": "Finance vs sales disagreement",
    "operations.churn_billing_cutoff": "Churn billing cutoff",
    "discounts.stacking_policy": "Discount stacking policy",
    "operations.credit_memo_process": "Credit memo process",
    "controls.invoice_price_qa": "Invoice price QA",
    "controls.billing_qa": "Pre-invoice billing QA",
    "controls.monthly_reconciliation": "Agreement reconciliation cadence",
}


def compute_sensitivity(
    normalized: dict[str, Any],
    posteriors: dict[str, float],
    priors: dict,
    segments: dict[str, float],
    answers: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    from estimator.modeling.pipeline import run_model

    arr = segments.get("arr", 0)
    if arr <= 0 or not answers:
        return _fallback_drivers(normalized)

    baseline = run_model(answers, random_seed=42, include_sensitivity=False)["estimate"]["central"]
    if baseline <= 0:
        return _fallback_drivers(normalized)

    drivers: list[dict[str, Any]] = []
    for key, (field, stressed_value) in PERTURBATIONS.items():
        if field not in answers and answers.get(field.split(".")[0]) is None:
            continue
        perturbed = dict(answers)
        perturbed[field] = stressed_value
        stressed = run_model(perturbed, random_seed=42, include_sensitivity=False)["estimate"]["central"]
        delta = max(stressed - baseline, 0)
        influence = min(delta / baseline, 1.0) if baseline > 0 else 0.0
        if influence <= 0:
            continue
        drivers.append(
            {
                "key": key,
                "label": DRIVER_LABELS.get(key, key),
                "influence": round(influence, 3),
                "delta_expected": round(delta),
            }
        )

    if not drivers:
        return _fallback_drivers(normalized)
    drivers.sort(key=lambda d: d["influence"], reverse=True)
    return drivers[:5]


def _fallback_drivers(normalized: dict[str, Any]) -> list[dict[str, Any]]:
    drivers: list[dict[str, Any]] = []
    for key, label in DRIVER_LABELS.items():
        if normalized.get(key) is None:
            continue
        drivers.append({"key": key, "label": label, "influence": 0.5})
    if not drivers:
        drivers = [
            {"key": "arr", "label": "Revenue scale (ARR)", "influence": 0.9},
            {"key": "complexity", "label": "Billing complexity", "influence": 0.7},
        ]
    drivers.sort(key=lambda d: d["influence"], reverse=True)
    return drivers[:5]
