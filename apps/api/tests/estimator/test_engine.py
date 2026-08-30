"""Estimator engine tests."""

from estimator.modeling.complexity import compute_complexity
from estimator.modeling.hypotheses import compute_posteriors
from estimator.modeling.monte_carlo import apply_correlation_adjustment, percentiles, simulate_totals
from estimator.modeling.normalize import derive_segments, normalize_answers
from estimator.modeling.pipeline import run_model
from estimator.questionnaire.engine import completion_progress, visible_question_ids
from estimator.questionnaire.schema import load_priors
from estimator.validation.checks import check_contradictions, check_sanity
import numpy as np


PROFILE_A = {
    "profile.company_type": "b2b_saas",
    "profile.arr_amount": 5_000_000,
    "profile.arr_confidence": "exact",
    "profile.customer_count": 200,
    "pricing.models": ["flat"],
    "pricing.usage_based": False,
    "pricing.seat_based": False,
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
    "changes.pricing_changes_24mo": "0",
    "changes.migration_method": "na",
    "systems.billing_system_count": "1",
    "systems.primary_platform": "stripe",
    "operations.manual_override_frequency": "never",
    "operations.manual_change_logging": "yes",
    "quote_to_bill.commercial_truth": "billing",
    "quote_to_bill.quote_automation": "fully",
    "migrations.migrated_36mo": False,
    "international.multi_currency": False,
    "controls.finance_team_size": "4_10",
    "controls.billing_owner": True,
    "controls.monthly_reconciliation": "monthly",
    "controls.billing_qa": "always",
    "velocity.commercial_changes_12mo": "0",
    "confidence.billing_confidence": 5,
    "confidence.last_reconciliation": "30d",
}

PROFILE_B = {
    **PROFILE_A,
    "profile.arr_amount": 25_000_000,
    "profile.customer_count": 120,
    "pricing.models": ["flat", "per_seat", "usage", "custom_enterprise", "addons"],
    "pricing.usage_based": True,
    "pricing.seat_based": True,
    "usage.unit_type": "api_calls",
    "usage.rating": "commit_overage",
    "usage.billing_timing": "monthly",
    "usage.reconciliation": "manual",
    "seats.reconciliation": "manual",
    "seats.true_up": False,
    "seats.self_service": False,
    "product.billable_count": "11_25",
    "product.independent_catalogs": "yes",
    "product.addons": True,
    "contracts.negotiated_arr_pct": "76_100",
    "contracts.custom_pricing": "yes",
    "contracts.grandfathering": "very_frequently",
    "contracts.renewal_increases": "manual",
    "discounts.frequency": "nearly_all",
    "discounts.expiry_handling": "manual_sales",
    "discounts.expiry_confidence": 1,
    "changes.pricing_changes_24mo": "6_plus",
    "changes.migration_method": "manual",
    "systems.billing_system_count": "3_plus",
    "operations.manual_override_frequency": "very_frequently",
    "operations.manual_change_logging": "no",
    "quote_to_bill.commercial_truth": "multiple",
    "quote_to_bill.quote_automation": "manual",
    "migrations.migrated_36mo": True,
    "migrations.reconciliation": "no",
    "migrations.parallel_systems": True,
    "international.multi_currency": True,
    "international.currency_count": "6_plus",
    "controls.billing_owner": False,
    "controls.monthly_reconciliation": "never",
    "controls.billing_qa": "rarely",
    "velocity.commercial_changes_12mo": "10_plus",
    "confidence.billing_confidence": 1,
    "confidence.last_reconciliation": "12mo_plus",
}

PROFILE_C = {
    **PROFILE_B,
    "operations.manual_override_frequency": "rarely",
    "operations.manual_change_logging": "yes",
    "quote_to_bill.quote_automation": "fully",
    "usage.reconciliation": "automated",
    "seats.reconciliation": "automatic",
    "controls.monthly_reconciliation": "monthly",
    "controls.billing_qa": "always",
    "discounts.expiry_handling": "automatic",
    "discounts.expiry_confidence": 5,
}


def test_visible_questions_skip_usage_branch_when_disabled():
    answers = {"pricing.usage_based": False, "pricing.seat_based": False}
    visible = visible_question_ids(answers)
    assert "usage.unit_type" not in visible
    assert "profile.company_type" in visible


def test_completion_progress_reaches_complete():
    progress = completion_progress(PROFILE_A)
    assert progress["is_complete"] is True


def test_profile_a_lower_exposure_than_profile_b():
    result_a = run_model(PROFILE_A, random_seed=42)
    result_b = run_model(PROFILE_B, random_seed=42)
    assert result_b["estimate"]["central"] > result_a["estimate"]["central"]


def test_profile_c_lower_than_profile_b():
    result_b = run_model(PROFILE_B, random_seed=7)
    result_c = run_model(PROFILE_C, random_seed=7)
    assert result_c["estimate"]["central"] < result_b["estimate"]["central"]


def test_reproducibility_same_seed():
    one = run_model(PROFILE_B, random_seed=99)
    two = run_model(PROFILE_B, random_seed=99)
    assert one["estimate"] == two["estimate"]


def test_arr_increase_does_not_decrease_estimate():
    low_arr = run_model({**PROFILE_A, "profile.arr_amount": 5_000_000}, random_seed=1)
    high_arr = run_model({**PROFILE_A, "profile.arr_amount": 10_000_000}, random_seed=1)
    assert high_arr["estimate"]["central"] >= low_arr["estimate"]["central"]


def test_anti_gaming_high_acv_warning():
    warnings = check_sanity({**PROFILE_A, "profile.arr_amount": 20_000_000, "profile.customer_count": 3})
    assert any(w["code"] == "high_acv" for w in warnings)


def test_leakage_capped_relative_to_arr():
    result = run_model({**PROFILE_B, "profile.arr_amount": 1_000_000}, random_seed=3)
    assert result["estimate"]["high"] <= 1_000_000 * 0.35 + 1


def test_correlation_adjustment_reduces_total():
    amounts = {"H1": 100_000.0, "H2": 90_000.0}
    priors = load_priors()
    adjusted, _ = apply_correlation_adjustment(amounts, priors["correlations"])
    assert adjusted < sum(amounts.values())


def test_monte_carlo_percentiles_ordered():
    priors = load_priors()
    normalized = normalize_answers(PROFILE_B)
    segments = derive_segments(normalized)
    posteriors = compute_posteriors(normalized, priors)
    rng = np.random.default_rng(1)
    totals, _, _ = simulate_totals(rng, segments["arr"], segments, posteriors, priors, 1000)
    pct = percentiles(totals)
    assert pct["p10"] <= pct["p50"] <= pct["p90"]


def test_contradiction_detects_usage_mismatch():
    conflicts = check_contradictions({"pricing.usage_based": False, "pricing.models": ["usage"]})
    assert len(conflicts) == 1


def test_complexity_separate_from_leakage():
    complexity = compute_complexity(normalize_answers(PROFILE_B))
    assert complexity["total"] > compute_complexity(normalize_answers(PROFILE_A))["total"]
