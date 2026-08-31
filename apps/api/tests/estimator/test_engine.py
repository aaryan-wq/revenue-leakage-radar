"""Estimator engine tests."""

from estimator.modeling.complexity import compute_complexity
from estimator.modeling.hypotheses import compute_posteriors
from estimator.modeling.monte_carlo import apply_correlation_adjustment, percentiles, simulate_totals
from estimator.modeling.normalize import derive_segments, normalize_answers
from estimator.modeling.pipeline import run_model
from estimator.modeling.rule_posteriors import compute_posteriors, compute_rule_posteriors
from estimator.questionnaire.engine import completion_progress, visible_question_ids
from estimator.questionnaire.schema import load_priors, load_rule_priors
from estimator.validation.checks import check_sanity
import numpy as np


PROFILE_A = {
    "profile.company_type": "b2b_saas",
    "profile.arr_amount": 5_000_000,
    "profile.arr_confidence": "exact",
    "profile.customer_count": 200,
    "quote_to_bill.finance_sales_disagreement": "never",
    "operations.unticketed_adjustments": "never",
    "pricing.models": ["flat"],
    "product.billable_count": "1",
    "product.independent_catalogs": "no",
    "product.addons": False,
    "contracts.negotiated_arr_pct": "0",
    "contracts.grandfathering": "never",
    "contracts.renewal_increases": "yes",
    "discounts.frequency": "never",
    "discounts.expiry_confidence": 5,
    "discounts.stacking_policy": "single",
    "changes.pricing_changes_24mo": "0",
    "changes.migration_method": "na",
    "systems.billing_system_count": "1",
    "systems.primary_platform": "stripe",
    "operations.manual_override_frequency": "never",
    "operations.credit_memo_process": "reviewed",
    "operations.churn_billing_cutoff": "same_day",
    "quote_to_bill.commercial_truth": "billing",
    "quote_to_bill.quote_automation": "fully",
    "migrations.migrated_36mo": False,
    "international.multi_currency": False,
    "controls.billing_owner": True,
    "controls.monthly_reconciliation": "monthly",
    "controls.billing_qa": "always",
    "controls.invoice_price_qa": "usually",
    "confidence.billing_confidence": 5,
}

PROFILE_B = {
    **PROFILE_A,
    "profile.arr_amount": 25_000_000,
    "profile.customer_count": 120,
    "pricing.models": ["flat", "per_seat", "usage", "custom_enterprise", "addons"],
    "usage.rating": "commit_overage",
    "usage.reconciliation": "manual",
    "seats.reconciliation": "manual",
    "product.billable_count": "11_25",
    "product.independent_catalogs": "yes",
    "product.addons": True,
    "contracts.negotiated_arr_pct": "76_100",
    "contracts.grandfathering": "very_frequently",
    "contracts.renewal_increases": "manual",
    "discounts.frequency": "nearly_all",
    "discounts.auto_expiry_removal": "never",
    "discounts.expiry_confidence": 1,
    "changes.pricing_changes_24mo": "6_plus",
    "changes.migration_method": "manual",
    "systems.billing_system_count": "3_plus",
    "operations.manual_override_frequency": "very_frequently",
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
    "controls.invoice_price_qa": "never",
    "operations.credit_memo_process": "ad_hoc",
    "operations.churn_billing_cutoff": "manual",
    "discounts.stacking_policy": "allowed",
    "confidence.billing_confidence": 1,
}

PROFILE_C = {
    **PROFILE_B,
    "operations.manual_override_frequency": "rarely",
    "quote_to_bill.quote_automation": "fully",
    "usage.reconciliation": "automated",
    "seats.reconciliation": "automatic",
    "controls.monthly_reconciliation": "monthly",
    "controls.billing_qa": "always",
    "discounts.auto_expiry_removal": "always",
    "discounts.expiry_confidence": 5,
}


def test_visible_questions_skip_usage_branch_when_disabled():
    answers = {"pricing.models": ["flat"]}
    visible = visible_question_ids(answers)
    assert "usage.unit_type" not in visible
    assert "usage.rating" not in visible
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
    rule_priors = load_rule_priors()
    normalized = normalize_answers(PROFILE_B)
    normalized["complexity.total"] = compute_complexity(normalized)["total"]
    segments = derive_segments(normalized)
    rule_posteriors = compute_rule_posteriors(normalized, rule_priors)
    rng = np.random.default_rng(1)
    totals, _, _, _, _, _ = simulate_totals(
        rng,
        segments["arr"],
        segments,
        rule_posteriors,
        priors,
        rule_priors,
        1000,
        normalized["complexity.total"],
        normalized,
    )
    pct = percentiles(totals)
    assert pct["p10"] <= pct["p50"] <= pct["p90"]


def test_complexity_separate_from_leakage():
    complexity = compute_complexity(normalize_answers(PROFILE_B))
    assert complexity["total"] > compute_complexity(normalize_answers(PROFILE_A))["total"]


def test_profile_b_headline_low_nonzero_when_central_positive():
    result = run_model(PROFILE_B, random_seed=42, scenario="central")
    assert result["estimate"]["central"] > 0
    assert result["estimate"]["low"] > 0


def test_scenario_bands_produce_different_ranges():
    conservative = run_model(PROFILE_B, random_seed=42, scenario="conservative")
    central = run_model(PROFILE_B, random_seed=42, scenario="central")
    aggressive = run_model(PROFILE_B, random_seed=42, scenario="aggressive")
    assert conservative["estimate"]["low"] <= central["estimate"]["low"]
    assert central["estimate"]["high"] <= aggressive["estimate"]["high"]
    assert conservative["estimate"]["high"] < aggressive["estimate"]["high"]


def test_default_scenario_is_aggressive():
    default_result = run_model(PROFILE_B, random_seed=42)
    aggressive = run_model(PROFILE_B, random_seed=42, scenario="aggressive")
    assert default_result["estimate"]["low"] == aggressive["estimate"]["low"]
    assert default_result["estimate"]["high"] == aggressive["estimate"]["high"]
    assert default_result["scenario"] == "aggressive"


def test_hypothesis_rows_have_expected_and_pct_arr():
    result = run_model(PROFILE_B, random_seed=42)
    assert result["top_hypotheses"]
    for item in result["top_hypotheses"]:
        assert item["expected"] > 0
        assert item["pct_of_arr"] > 0
        assert item["likelihood"] > 0
        assert not (item["low"] == 0 and item["high"] == 0 and item["expected"] > 0)


def test_insights_include_answer_specific_content():
    result = run_model(PROFILE_B, random_seed=42)
    assert result.get("profile_summary")
    assert result["profile_summary"]["risk_flags"]
    insights_text = " ".join(m["insight"].lower() for m in result.get("mechanism_insights", []))
    rule_text = " ".join(m["insight"].lower() for m in result.get("rule_insights", []))
    combined = f"{insights_text} {rule_text}"
    assert "grandfather" in " ".join(result["profile_summary"]["risk_flags"]).lower() or "grandfather" in combined
    assert result.get("calculation_summary")
    assert result["calculation_summary"]["explanation_bullets"]
    assert result.get("verification_preview")
    assert result.get("rule_breakdown")
    assert len(result["rule_breakdown"]) >= 10


def test_clean_profile_expected_uses_simulation_mean():
    answers = {**PROFILE_A, "profile.arr_amount": 18_000_000, "profile.customer_count": 1200}
    result = run_model(answers, random_seed=42)
    assert result["estimate"]["central"] > 0
    assert result["calculation_summary"]["pct_runs_with_leakage"] > 0


def test_calibration_fixtures_within_tolerance():
    from tests.estimator.calibration_fixtures import CALIBRATION_CASES

    errors: list[float] = []
    for case in CALIBRATION_CASES:
        result = run_model(case["answers"], random_seed=42)
        model = result["estimate"]["central"]
        justified = case["justified_leakage_usd"]
        errors.append(abs((model - justified) / justified * 100))
    assert sum(errors) / len(errors) <= 12.0
    assert max(errors) <= 26.0


def test_rule_breakdown_covers_many_rules_for_messy_profile():
    result = run_model(PROFILE_B, random_seed=42)
    active_rules = [row for row in result.get("rule_breakdown", []) if row["expected"] > 0]
    assert len(active_rules) >= 15
    assert result["estimate"]["central"] <= result["theoretical_stack"]["p90"] + 1


def test_overlap_sanity_expected_lte_stack():
    result = run_model(PROFILE_B, random_seed=42)
    assert result["estimate"]["central"] <= result["theoretical_stack"]["p90"] + 1
    assert result["estimate"].get("recoverable", 0) <= result["estimate"]["central"]


def test_display_rollups_present():
    result = run_model(PROFILE_B, random_seed=42)
    rollups = result.get("display_rollups", [])
    assert rollups
    assert any(item["rollup_id"] == "H19" for item in rollups)


def test_stale_result_detects_old_calibration_stage():
    from estimator.modeling.fingerprint import is_stale_result

    fresh = run_model(PROFILE_B, random_seed=42)
    assert is_stale_result(fresh) is False
    assert is_stale_result({"model_version": fresh["model_version"], "calibration_stage": 0}) is True
    assert is_stale_result({"model_version": "0.0.0", "calibration_stage": fresh["calibration_stage"]}) is True


def test_headline_metrics_ordering():
    result = run_model(PROFILE_B, random_seed=42, scenario="central")
    pct = result["percentiles"]
    est = result["estimate"]
    assert pct["p10"] <= est["low"] <= est["central"] <= est["high"] <= pct["p90"]
    assert est.get("gross_expected", 0) >= est["central"]


def test_benchmark_never_overwrites_central():
    from tests.estimator.calibration_fixtures import MERIDIAN_MODERATE, PROFILE_A

    low = run_model({**PROFILE_A, "profile.arr_amount": 5_000_000}, random_seed=42)
    high = run_model(MERIDIAN_MODERATE, random_seed=42)
    for result in (low, high):
        context = result.get("benchmark_context")
        if context is None:
            continue
        assert result["estimate"]["central"] == result["estimate"]["net_recoverable"]
        if context["may_understate"]:
            assert result["estimate"]["central"] < context["low_usd"]
        assert result["estimate"]["central"] != context["low_usd"] or result["estimate"]["central"] == 0


def test_meridian_moderate_min_pct():
    from tests.estimator.calibration_fixtures import MERIDIAN_MODERATE

    result = run_model(MERIDIAN_MODERATE, random_seed=42)
    arr = result["arr_usd"]
    pct = (result["estimate"]["central"] / arr) * 100 if arr else 0
    assert pct >= 0.8

