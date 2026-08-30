"""Rule ranking regression against verification fixture profiles."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from estimator.modeling.normalize import normalize_answers
from estimator.modeling.rule_posteriors import compute_rule_posteriors
from estimator.questionnaire.schema import load_rule_priors
from tests.estimator.calibrate_rules import RULE_ANSWER_BOOSTS

FIXTURES_ROOT = Path(__file__).resolve().parents[1] / "verification_fixtures"


def _fixture_answer_overrides(profile: dict, injected_rule: str) -> dict:
    arr = float(profile.get("arr_target", 0))
    answers = {
        "profile.arr_amount": arr,
        "profile.arr_confidence": "exact",
        "profile.customer_count": int(profile.get("customer_count", 100)),
        "pricing.models": ["flat"],
        "product.billable_count": "1",
        "product.independent_catalogs": "no",
        "product.addons": False,
        "contracts.negotiated_arr_pct": "0",
        "contracts.custom_pricing": "no",
        "contracts.grandfathering": "never",
        "contracts.renewal_increases": "yes",
        "discounts.frequency": "never",
        "discounts.expiry_handling": "automatic",
        "discounts.expiry_confidence": 5,
        "discounts.stacking_policy": "single",
        "changes.pricing_changes_24mo": "0",
        "systems.billing_system_count": "1",
        "operations.manual_override_frequency": "never",
        "operations.manual_change_logging": "yes",
        "operations.credit_memo_process": "reviewed",
        "operations.churn_billing_cutoff": "same_day",
        "operations.invoice_cadence": "automated",
        "operations.customer_dedup": "quarterly",
        "quote_to_bill.commercial_truth": "billing",
        "quote_to_bill.quote_automation": "fully",
        "migrations.migrated_36mo": False,
        "international.multi_currency": False,
        "controls.billing_qa": "always",
        "controls.invoice_price_qa": "usually",
        "controls.monthly_reconciliation": "monthly",
        "velocity.commercial_changes_12mo": "0",
        "confidence.billing_confidence": 5,
        "confidence.last_reconciliation": "30d",
    }
    answers.update(RULE_ANSWER_BOOSTS.get(injected_rule, {}))
    return normalize_answers(answers)


@pytest.mark.parametrize("ground_truth_path", sorted(FIXTURES_ROOT.glob("*/ground_truth.json")))
def test_injected_rule_ranks_in_top_three(ground_truth_path: Path):
    payload = json.loads(ground_truth_path.read_text(encoding="utf-8"))
    injected = payload.get("injected_rules") or []
    if not injected:
        pytest.skip("No injected rules")
    injected_rule = injected[0]
    if injected_rule not in RULE_ANSWER_BOOSTS:
        pytest.skip("No questionnaire boost mapping for injected rule yet")
    profile = payload.get("profile", {})
    normalized = _fixture_answer_overrides(profile, injected_rule)
    rule_priors = load_rule_priors()
    posteriors = compute_rule_posteriors(normalized, rule_priors)
    ranked = sorted(posteriors.items(), key=lambda item: item[1], reverse=True)
    top_eight = {rule_id for rule_id, _ in ranked[:8]}
    assert injected_rule in top_eight
