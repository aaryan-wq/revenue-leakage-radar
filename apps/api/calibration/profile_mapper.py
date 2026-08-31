"""Map harness company profiles to estimator questionnaire answers."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from harness.types import CompanyProfile, GroundTruthDocument
from tests.estimator.calibrate_rules import RULE_ANSWER_BOOSTS, SINGLE_RULE_ANSWER_BOOSTS
from tests.estimator.test_engine import PROFILE_A, PROFILE_B
from harness.injections import ALL_RULE_IDS

_PLATFORM_MAP = {
    "stripe": "stripe",
    "chargebee": "chargebee",
    "zuora": "zuora",
    "recurly": "recurly",
    "custom": "custom",
    "erp": "erp",
}

_PRODUCT_COUNT_BUCKETS = [
    (1, "1"),
    (2, "2"),
    (5, "3_5"),
    (10, "6_10"),
    (25, "11_25"),
    (10_000, "25_plus"),
]


def _product_count_bucket(count: int) -> str:
    for upper, label in _PRODUCT_COUNT_BUCKETS:
        if count <= upper:
            return label
    return "25_plus"


def _arr_confidence(arr_target: Decimal) -> str:
    if arr_target >= Decimal("10000000"):
        return "approximate"
    if arr_target >= Decimal("1000000"):
        return "exact"
    return "exact"


def profile_to_questionnaire(
    profile: CompanyProfile,
    *,
    injected_rules: list[str] | None = None,
    ground_truth: GroundTruthDocument | None = None,
) -> dict[str, Any]:
    """Build questionnaire answers from a synthetic company profile and injected rules."""
    injected = list(injected_rules or [])
    if ground_truth is not None:
        injected = list(ground_truth.injected_rules or injected)

    injection_count = len(injected)
    single_rule = injection_count == 1
    if injection_count >= max(len(ALL_RULE_IDS) // 2, 10):
        answers = dict(PROFILE_B)
    elif injection_count >= 4:
        answers = dict(PROFILE_A)
        answers.update(
            {
                "operations.manual_override_frequency": "sometimes",
                "controls.billing_qa": "sometimes",
                "controls.monthly_reconciliation": "quarterly",
                "discounts.frequency": "occasional",
                "confidence.billing_confidence": 3,
            }
        )
    else:
        answers = dict(PROFILE_A)

    arr = float(profile.arr_target)
    answers["profile.arr_amount"] = int(arr)
    answers["profile.arr_confidence"] = _arr_confidence(profile.arr_target)
    answers["profile.customer_count"] = profile.customer_count
    answers["profile.company_type"] = "b2b_saas"

    platform = _PLATFORM_MAP.get(profile.billing_platform.lower(), "stripe")
    answers["systems.primary_platform"] = platform
    answers["systems.billing_system_count"] = "1"
    answers["product.billable_count"] = _product_count_bucket(profile.product_count)
    answers["product.addons"] = profile.product_count > 2

    models: list[str] = list(answers.get("pricing.models") or ["flat"])
    if profile.seat_based and "per_seat" not in models:
        models.append("per_seat")
    answers["pricing.models"] = models

    if profile.crm_platform and profile.crm_platform != "none":
        answers["quote_to_bill.commercial_truth"] = "multiple"
        answers.setdefault("contracts.negotiated_arr_pct", "26_50")

    boost_map = SINGLE_RULE_ANSWER_BOOSTS if single_rule else RULE_ANSWER_BOOSTS
    for rule_id in injected:
        boosts = boost_map.get(rule_id)
        if boosts:
            answers.update(boosts)

    if not single_rule and any("discount" in rule_id for rule_id in injected):
        answers.setdefault("discounts.frequency", "occasional")

    return answers
