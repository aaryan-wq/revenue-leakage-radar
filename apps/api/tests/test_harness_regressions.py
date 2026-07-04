"""Replay saved harness regression cases by regenerating companies from meta seeds."""

from __future__ import annotations

import pytest

from harness.comparator import compare_findings
from harness.company_generator import generate_company
from harness.context_loader import build_context_from_state
from harness.engine_runner import run_all_rules
from harness.regression import list_regression_cases


from harness.injections import INJECTORS


@pytest.mark.parametrize(
    "case",
    [case for case in list_regression_cases() if case.rule_id in INJECTORS],
    ids=lambda case: case.case_id,
)
def test_regression_case_replay(case):
    company = generate_company(
        seed=case.seed,
        customer_count=80,
        rule_ids=[case.rule_id],
    )
    ctx, id_maps = build_context_from_state(company.rows())
    engine = run_all_rules(ctx, rule_ids=[case.rule_id])
    assert not engine.errors, f"Engine errors: {engine.errors}"

    comparison = compare_findings(
        company.ground_truth.findings,
        engine.findings,
        id_maps,
        allow_extra=True,
    )
    rule_expected = [f for f in company.ground_truth.findings if f.rule_id == case.rule_id]
    assert rule_expected
    assert comparison.matched >= len(rule_expected), comparison.summary()
