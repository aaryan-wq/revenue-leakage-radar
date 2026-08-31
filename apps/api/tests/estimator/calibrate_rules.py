"""Parse verification fixture ground truth for rule-level calibration anchors."""

from __future__ import annotations

import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

FIXTURES_ROOT = Path(__file__).resolve().parents[1] / "verification_fixtures"

RULE_ANSWER_BOOSTS: dict[str, dict[str, object]] = {
    "expired_discount": {
        "discounts.frequency": "common",
        "discounts.expiry_handling": "manual_finance",
        "discounts.stacking_policy": "allowed",
    },
    "grandfathered_pricing": {"contracts.grandfathering": "very_frequently"},
    "legacy_pricing": {"changes.pricing_changes_24mo": "4_5"},
    "renewal_price_drift": {"contracts.renewal_increases": "manual"},
    "manual_price_override": {"operations.manual_override_frequency": "very_frequently"},
    "price_catalog_mismatch": {"product.billable_count": "6_10", "changes.pricing_changes_24mo": "2_3"},
    "discount_stacking": {"discounts.stacking_policy": "allowed", "discounts.frequency": "common"},
    "duplicate_discount": {"discounts.stacking_policy": "allowed", "discounts.frequency": "common"},
    "excessive_discount": {"discounts.stacking_policy": "allowed", "discounts.frequency": "nearly_all"},
    "invoice_price_mismatch": {
        "controls.invoice_price_qa": "never",
        "controls.billing_qa": "never",
    },
    "cancelled_subscription_still_billing": {"operations.churn_billing_cutoff": "manual"},
    "credit_leakage": {"operations.credit_memo_process": "ad_hoc"},
}

# Milder questionnaire signals for single-rule verification companies (mostly clean baseline).
SINGLE_RULE_ANSWER_BOOSTS: dict[str, dict[str, object]] = {
    "expired_discount": {
        "discounts.frequency": "occasional",
        "discounts.expiry_handling": "manual_finance",
        "discounts.stacking_policy": "limited",
    },
    "grandfathered_pricing": {"contracts.grandfathering": "sometimes"},
    "legacy_pricing": {"changes.pricing_changes_24mo": "2_3"},
    "renewal_price_drift": {"contracts.renewal_increases": "manual"},
    "missing_scheduled_increase": {"contracts.renewal_increases": "manual"},
    "manual_price_override": {"operations.manual_override_frequency": "sometimes"},
    "price_catalog_mismatch": {"product.billable_count": "3_5", "changes.pricing_changes_24mo": "1"},
    "discount_stacking": {"discounts.stacking_policy": "limited", "discounts.frequency": "occasional"},
    "duplicate_discount": {"discounts.stacking_policy": "limited", "discounts.frequency": "occasional"},
    "excessive_discount": {"discounts.stacking_policy": "limited", "discounts.frequency": "occasional"},
    "invoice_price_mismatch": {
        "controls.invoice_price_qa": "sometimes",
        "controls.billing_qa": "sometimes",
    },
    "cancelled_subscription_still_billing": {"operations.churn_billing_cutoff": "within_week"},
    "credit_leakage": {"operations.credit_memo_process": "manual"},
    "duplicate_credit": {"operations.credit_memo_process": "manual"},
    "contract_billing_price_divergence": {
        "quote_to_bill.commercial_truth": "billing",
        "contracts.custom_pricing": "some",
    },
    "incorrect_seat_price": {"pricing.models": ["flat", "per_seat"], "seats.reconciliation": "manual"},
    "incorrect_addon_price": {"product.addons": True},
    "discount_wrong_product": {"discounts.frequency": "occasional"},
    "missing_expected_invoice": {"operations.invoice_cadence": "scheduled"},
}


def load_fixture_anchors() -> dict[str, list[float]]:
    """Return rule_id -> list of annual_leakage/arr_target ratios from fixtures."""
    ratios: dict[str, list[float]] = defaultdict(list)
    for ground_truth_path in FIXTURES_ROOT.glob("*/ground_truth.json"):
        payload = json.loads(ground_truth_path.read_text(encoding="utf-8"))
        arr_target = Decimal(str(payload.get("profile", {}).get("arr_target", "0")))
        if arr_target <= 0:
            continue
        for finding in payload.get("findings", []):
            if finding.get("is_negative"):
                continue
            rule_id = finding.get("rule_id")
            annual = Decimal(str(finding.get("expected_annual_leakage", "0")))
            if rule_id and annual > 0:
                ratios[rule_id].append(float(annual / arr_target))
    return dict(ratios)


def median_ratio(rule_id: str) -> float | None:
    values = load_fixture_anchors().get(rule_id)
    if not values:
        return None
    values = sorted(values)
    mid = len(values) // 2
    return values[mid]


def summarize_anchors() -> list[tuple[str, float, int]]:
    anchors = load_fixture_anchors()
    summary: list[tuple[str, float, int]] = []
    for rule_id, values in sorted(anchors.items()):
        values = sorted(values)
        summary.append((rule_id, values[len(values) // 2], len(values)))
    return summary


if __name__ == "__main__":
    for rule_id, median, count in summarize_anchors():
        print(f"{rule_id:<40} median_ratio={median:.4f} fixtures={count}")
