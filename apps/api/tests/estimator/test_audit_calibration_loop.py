"""Smoke tests for audit-driven estimator calibration loop."""

from __future__ import annotations

from calibration.cases import build_cases_from_single_rules
from calibration.compare import compare_cases
from calibration.tune import compute_rule_prior_adjustments


def test_audit_calibration_loop_generated_single_rules_smoke():
    cases = build_cases_from_single_rules(base_seed=42, max_audit_delta_pct=25.0)[:6]
    assert cases, "Expected generated single-rule verification companies"
    rows, _ = compare_cases(cases, random_seed=42)
    assert len(rows) == len(cases)
    assert all(row.audit_target_usd > 0 for row in rows)
    adjustments = compute_rule_prior_adjustments(cases, rows)
    assert adjustments, "Expected audit/estimator ratios for single-rule cases"
