"""Automated verification harness tests, fuzz every deterministic rule."""

from __future__ import annotations

import random
import time

import pytest

from harness.comparator import compare_findings
from harness.company_generator import generate_company
from harness.context_loader import build_context_from_state
from harness.csv_fuzzer import CsvFuzzConfig
from harness.engine_runner import run_all_rules
from harness.injections import ALL_RULE_IDS, INJECTORS
from harness.runner import run_harness, HarnessConfig

COMPANY_SIZES = [30, 50, 100]


@pytest.mark.parametrize("rule_id", ALL_RULE_IDS)
def test_each_rule_injection_detected(rule_id: str):
    """Each rule must fire with exact financial ground truth on a focused dataset."""
    seed = abs(hash(rule_id)) % (2**28)
    company = generate_company(
        seed=seed,
        customer_count=80,
        product_count=4,
        rule_ids=[rule_id],
    )
    ctx, id_maps = build_context_from_state(company.rows())
    engine = run_all_rules(ctx, rule_ids=[rule_id])

    assert not engine.errors, f"Engine errors: {engine.errors}"

    comparison = compare_findings(
        company.ground_truth.findings,
        engine.findings,
        id_maps,
        allow_extra=False,
    )
    rule_expected = [f for f in company.ground_truth.findings if f.rule_id == rule_id]
    assert rule_expected, f"No ground truth recorded for {rule_id}"
    assert comparison.matched >= len(rule_expected), comparison.summary()


@pytest.mark.parametrize("customer_count", COMPANY_SIZES)
def test_full_rule_suite_at_scale(customer_count: int):
    """All 20 rules injected together must match ground truth."""
    company = generate_company(
        seed=1000 + customer_count,
        customer_count=customer_count,
        rule_ids=ALL_RULE_IDS,
    )
    ctx, id_maps = build_context_from_state(company.rows())
    engine = run_all_rules(ctx)
    assert not engine.errors

    comparison = compare_findings(
        company.ground_truth.findings,
        engine.findings,
        id_maps,
        allow_extra=True,
    )
    assert comparison.passed, comparison.summary()


@pytest.mark.parametrize("billing_platform", ["stripe", "chargebee", "zuora", "paddle", "hubspot"])
def test_csv_fuzz_export_preserves_context(billing_platform: str):
    """Fuzzed CSV export + reload should still produce findings."""
    company = generate_company(seed=42, customer_count=30, rule_ids=["price_catalog_mismatch"])
    rng = random.Random(99)
    fuzz = CsvFuzzConfig(platform=billing_platform, header_style="random", shuffle_columns=True)
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        company.export_csvs(Path(tmp), rng, fuzz)
        ctx, id_maps = build_context_from_state(company.rows())
        engine = run_all_rules(ctx, rule_ids=["price_catalog_mismatch"])
        comparison = compare_findings(
            company.ground_truth.findings,
            engine.findings,
            id_maps,
            allow_extra=True,
        )
        assert comparison.matched >= 1, comparison.summary()


def test_harness_batch_stability():
    """Repeated randomized iterations should pass within performance budget."""
    start = time.perf_counter()
    result = run_harness(
        HarnessConfig(
            iterations=50,
            customer_count=40,
            rule_ids=ALL_RULE_IDS,
            seed=777,
            fuzz_csv=False,
            save_failures=False,
            allow_extra_findings=True,
        )
    )
    elapsed = time.perf_counter() - start
    assert elapsed < 120, f"Harness too slow: {elapsed:.1f}s"
    assert result.iterations_passed >= result.iterations_run - 1, (
        f"Only {result.iterations_passed}/{result.iterations_run} passed; "
        f"mismatches={result.total_mismatches} errors={result.errors}"
    )


@pytest.mark.parametrize("rule_id", list(INJECTORS.keys()))
def test_injector_registered(rule_id: str):
    assert rule_id in ALL_RULE_IDS
