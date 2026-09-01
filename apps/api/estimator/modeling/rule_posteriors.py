"""Declarative rule-level posterior computation from questionnaire answers."""

from __future__ import annotations

from typing import Any

from estimator.modeling.hypotheses import HYPOTHESIS_IDS, compute_posteriors as compute_legacy_hypothesis_posteriors
from estimator.questionnaire.schema import load_rule_priors


RULE_QUESTION_DRIVERS: dict[str, dict[str, dict[str, float]]] = {
    "legacy_pricing": {
        "contracts.grandfathering": {
            "never": 0.5,
            "rarely": 0.8,
            "sometimes": 1.2,
            "frequently": 1.8,
            "very_frequently": 2.5,
            "unknown": 1.3,
        },
        "changes.pricing_changes_24mo": {
            "0": 0.6,
            "1": 1.0,
            "2_3": 1.4,
            "4_5": 1.8,
            "6_plus": 2.2,
        },
    },
    "grandfathered_pricing": {
        "contracts.grandfathering": {
            "never": 0.4,
            "rarely": 0.7,
            "sometimes": 1.3,
            "frequently": 2.0,
            "very_frequently": 2.8,
            "unknown": 1.4,
        },
    },
    "renewal_price_drift": {
        "contracts.renewal_increases": {
            "yes": 0.6,
            "manual": 1.8,
            "no": 1.2,
            "unknown": 1.3,
        },
        "changes.pricing_changes_24mo": {
            "0": 0.6,
            "1": 1.0,
            "2_3": 1.4,
            "4_5": 1.8,
            "6_plus": 2.2,
        },
    },
    "missing_scheduled_increase": {
        "contracts.renewal_increases": {"yes": 0.5, "manual": 2.0, "no": 1.3, "unknown": 1.4},
    },
    "expired_discount": {
        "discounts.frequency": {
            "never": 0.3,
            "rare": 0.7,
            "occasional": 1.2,
            "common": 1.8,
            "nearly_all": 2.5,
        },
        "discounts.auto_expiry_removal": {
            "always": 0.5,
            "usually": 0.7,
            "sometimes": 1.2,
            "rarely": 1.6,
            "never": 2.0,
            "unknown": 1.4,
        },
    },
    "discount_stacking": {
        "discounts.frequency": {
            "never": 0.2,
            "rare": 0.6,
            "occasional": 1.3,
            "common": 2.0,
            "nearly_all": 2.8,
        },
        "discounts.stacking_policy": {
            "never": 0.3,
            "single": 0.7,
            "limited": 1.0,
            "allowed": 1.8,
            "unknown": 1.5,
        },
    },
    "duplicate_discount": {
        "discounts.frequency": {
            "never": 0.2,
            "rare": 0.6,
            "occasional": 1.2,
            "common": 1.9,
            "nearly_all": 2.6,
        },
        "discounts.stacking_policy": {
            "never": 0.4,
            "single": 0.8,
            "limited": 1.2,
            "allowed": 2.0,
            "unknown": 1.4,
        },
    },
    "excessive_discount": {
        "discounts.frequency": {
            "never": 0.2,
            "rare": 0.5,
            "occasional": 1.1,
            "common": 1.7,
            "nearly_all": 2.4,
        },
        "discounts.stacking_policy": {
            "never": 0.5,
            "single": 0.9,
            "limited": 1.1,
            "allowed": 1.9,
            "unknown": 1.3,
        },
    },
    "permanent_promotional_discount": {
        "discounts.frequency": {
            "never": 0.3,
            "rare": 0.7,
            "occasional": 1.2,
            "common": 1.8,
            "nearly_all": 2.5,
        },
        "discounts.expiry_confidence": {"scale": 0.15, "invert": True, "base": 1.0},
    },
    "manual_price_override": {
        "operations.manual_override_frequency": {
            "never": 0.4,
            "rarely": 0.8,
            "sometimes": 1.4,
            "frequently": 2.0,
            "very_frequently": 2.8,
            "unknown": 1.3,
        },
    },
    "invoice_price_mismatch": {
        "controls.invoice_price_qa": {
            "always": 0.4,
            "usually": 0.6,
            "sometimes": 1.2,
            "rarely": 1.8,
            "never": 2.2,
            "unknown": 1.4,
        },
        "operations.manual_override_frequency": {
            "never": 0.5,
            "rarely": 0.8,
            "sometimes": 1.3,
            "frequently": 1.9,
            "very_frequently": 2.5,
            "unknown": 1.2,
        },
    },
    "incorrect_seat_price": {
        "seats.reconciliation": {"automatic": 0.6, "manual": 1.8, "unknown": 1.4},
        "pricing.seat_based": {"true": 1.8, "false": 0.4},
    },
    "usage_billing_drift": {
        "usage.reconciliation": {"automated": 0.5, "partial": 1.0, "manual": 1.8, "unknown": 1.4},
        "pricing.usage_based": {"true": 2.0, "false": 0.3},
    },
    "active_subscription_not_billing": {
        "operations.churn_billing_cutoff": {
            "immediate": 0.4,
            "same_day": 0.5,
            "within_week": 0.9,
            "manual": 1.8,
            "unknown": 1.5,
        },
        "pricing.usage_based": {"true": 1.6, "false": 0.8},
    },
    "cancelled_subscription_still_billing": {
        "operations.churn_billing_cutoff": {
            "immediate": 0.3,
            "same_day": 0.4,
            "within_week": 0.8,
            "manual": 2.0,
            "unknown": 1.6,
        },
    },
    "missing_expected_invoice": {
        "controls.invoice_price_qa": {
            "always": 0.4,
            "usually": 0.6,
            "sometimes": 1.2,
            "rarely": 1.8,
            "never": 2.2,
            "unknown": 1.4,
        },
    },
    "credit_leakage": {
        "operations.credit_memo_process": {
            "automated": 0.4,
            "reviewed": 0.7,
            "manual": 1.6,
            "ad_hoc": 2.2,
            "unknown": 1.5,
        },
    },
    "duplicate_credit": {
        "operations.credit_memo_process": {
            "automated": 0.3,
            "reviewed": 0.6,
            "manual": 1.7,
            "ad_hoc": 2.3,
            "unknown": 1.5,
        },
    },
    "duplicate_customer": {
        "systems.billing_system_count": {
            "1": 0.6,
            "2": 1.2,
            "3_plus": 1.8,
            "unknown": 1.3,
        },
    },
    "contract_billing_price_divergence": {
        "contracts.negotiated_arr_pct": {
            "0": 0.4,
            "1_25": 0.8,
            "26_50": 1.2,
            "51_75": 1.7,
            "76_100": 2.2,
        },
        "quote_to_bill.quote_automation": {
            "fully": 0.5,
            "mostly": 0.7,
            "partial": 1.2,
            "mostly_manual": 1.8,
            "manual": 2.2,
            "unknown": 1.4,
        },
        "quote_to_bill.commercial_truth": {
            "crm": 1.0,
            "billing": 0.7,
            "cpq": 0.85,
            "contracts": 0.9,
            "spreadsheet": 1.4,
            "multiple": 1.6,
            "undefined": 1.7,
        },
    },
    "price_catalog_mismatch": {
        "product.billable_count": {
            "1": 0.5,
            "2": 0.8,
            "3_5": 1.1,
            "6_10": 1.5,
            "11_25": 2.0,
            "25_plus": 2.5,
        },
        "changes.pricing_changes_24mo": {
            "0": 0.6,
            "1": 1.0,
            "2_3": 1.4,
            "4_5": 1.8,
            "6_plus": 2.2,
        },
    },
    "incorrect_addon_price": {
        "product.addons": {"true": 1.8, "false": 0.4},
        "product.billable_count": {
            "1": 0.5,
            "2": 0.8,
            "3_5": 1.1,
            "6_10": 1.5,
            "11_25": 2.0,
            "25_plus": 2.5,
        },
    },
    "discount_wrong_product": {
        "product.billable_count": {
            "1": 0.5,
            "2": 0.8,
            "3_5": 1.2,
            "6_10": 1.6,
            "11_25": 2.1,
            "25_plus": 2.6,
        },
    },
    "duplicate_subscription": {
        "migrations.migrated_36mo": {"true": 2.0, "false": 0.7},
        "migrations.parallel_systems": {"true": 1.5, "false": 0.9},
        "systems.billing_system_count": {
            "1": 0.6,
            "2": 1.0,
            "3_plus": 1.4,
            "unknown": 1.0,
        },
    },
    "orphaned_records": {
        "migrations.migrated_36mo": {"true": 2.0, "false": 0.7},
        "migrations.parallel_systems": {"true": 1.5, "false": 0.9},
        "systems.billing_system_count": {
            "1": 0.6,
            "2": 1.0,
            "3_plus": 1.4,
            "unknown": 1.0,
        },
    },
    "currency_mismatch": {
        "international.multi_currency": {"true": 2.0, "false": 0.4},
    },
    "billing_frequency_mismatch": {
        "contracts.negotiated_arr_pct": {
            "0": 0.5,
            "1_25": 0.8,
            "26_50": 1.1,
            "51_75": 1.5,
            "76_100": 1.9,
        },
    },
}

BILLING_EXECUTION_RULES = {
    "active_subscription_not_billing",
    "cancelled_subscription_still_billing",
    "missing_expected_invoice",
    "invoice_price_mismatch",
}

BILLING_EXECUTION_DRIVERS: dict[str, dict[str, float]] = {
    "controls.billing_qa": {
        "always": 0.5,
        "usually": 0.7,
        "sometimes": 1.1,
        "rarely": 1.5,
        "never": 1.9,
        "unknown": 1.2,
    },
    "controls.monthly_reconciliation": {
        "monthly": 0.6,
        "quarterly": 0.9,
        "occasionally": 1.2,
        "never": 1.7,
        "unknown": 1.1,
    },
}


# Minimum LR for control answers that over-suppress leakage (e.g. "always" auto-removal).
DRIVER_LR_FLOORS: dict[str, dict[str, float]] = {
    "expired_discount": {"discounts.auto_expiry_removal": 0.7},
}


def get_rule_ids(rule_priors: dict[str, Any] | None = None) -> list[str]:
    data = rule_priors or load_rule_priors()
    return sorted(data.get("rules", {}).keys())


def _likelihood_from_drivers(
    rule_id: str,
    normalized: dict[str, Any],
    drivers: dict[str, dict[str, float]],
) -> float:
    lr = 1.0
    rule_drivers = drivers.get(rule_id) or RULE_QUESTION_DRIVERS.get(rule_id, {})
    for question_key, mapping in rule_drivers.items():
        if "scale" in mapping:
            value = normalized.get(question_key)
            if value is not None:
                try:
                    numeric = float(value)
                    if mapping.get("invert"):
                        lr *= mapping.get("base", 1.0) + (5 - numeric) * mapping["scale"]
                    else:
                        lr *= mapping.get("base", 1.0) + numeric * mapping["scale"]
                except (TypeError, ValueError):
                    pass
            continue
        value = normalized.get(question_key)
        if value is None:
            continue
        if isinstance(value, bool):
            key = "true" if value else "false"
            mult = mapping.get(key, 1.0)
        else:
            mult = mapping.get(str(value), 1.0)
        floor = DRIVER_LR_FLOORS.get(rule_id, {}).get(question_key)
        if floor is not None:
            mult = max(mult, floor)
        lr *= mult

    billing_conf = normalized.get("confidence.billing_confidence")
    if billing_conf is not None:
        try:
            lr *= 1.0 + (5 - float(billing_conf)) * 0.06
        except (TypeError, ValueError):
            pass
    return max(lr, 0.1)


def compute_rule_posteriors(
    normalized: dict[str, Any],
    rule_priors: dict[str, Any] | None = None,
) -> dict[str, float]:
    data = rule_priors or load_rule_priors()
    rules_cfg = data.get("rules", {})
    result: dict[str, float] = {}
    for rule_id, cfg in rules_cfg.items():
        prior = float(cfg.get("prior", 0.03))
        odds = prior / max(1 - prior, 1e-6)
        yaml_drivers = cfg.get("question_drivers") or {}
        merged_drivers = {**RULE_QUESTION_DRIVERS.get(rule_id, {}), **yaml_drivers}
        if rule_id in BILLING_EXECUTION_RULES:
            merged_drivers = {**merged_drivers, **BILLING_EXECUTION_DRIVERS}
        odds *= _likelihood_from_drivers(rule_id, normalized, {rule_id: merged_drivers})
        posterior = odds / (1 + odds)
        result[rule_id] = min(max(posterior, 0.001), 0.95)
    return result


def compute_hypothesis_posteriors_from_rules(
    rule_posteriors: dict[str, float],
    rule_priors: dict[str, Any] | None = None,
) -> dict[str, float]:
    """Aggregate rule posteriors to hypothesis level (max of child rules)."""
    data = rule_priors or load_rule_priors()
    rules_cfg = data.get("rules", {})
    result: dict[str, float] = {}
    for hid in HYPOTHESIS_IDS:
        child_probs = [
            rule_posteriors[rule_id]
            for rule_id, cfg in rules_cfg.items()
            if hid in cfg.get("hypothesis_ids", [])
        ]
        if child_probs:
            # Noisy-OR combination of child rule probabilities
            combined = 1.0
            for p in child_probs:
                combined *= 1 - p
            result[hid] = min(max(1 - combined, 0.001), 0.95)
        else:
            result[hid] = 0.05
    return result


def compute_posteriors(normalized: dict[str, Any], priors: dict[str, Any]) -> dict[str, float]:
    """Backward-compatible hypothesis posteriors; prefers rule-native aggregation."""
    rule_posteriors = compute_rule_posteriors(normalized)
    from_rules = compute_hypothesis_posteriors_from_rules(rule_posteriors)
    legacy = compute_legacy_hypothesis_posteriors(normalized, priors)
    blended: dict[str, float] = {}
    for hid in HYPOTHESIS_IDS:
        blended[hid] = min(max((from_rules.get(hid, 0.05) * 0.55 + legacy.get(hid, 0.05) * 0.45), 0.001), 0.95)
    return blended
