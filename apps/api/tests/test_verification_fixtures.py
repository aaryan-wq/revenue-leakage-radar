"""Deterministic verification fixture tests, engine must match ground truth exactly."""

from __future__ import annotations

import pytest

from harness.fixture_catalog import FIXTURE_CATALOG, all_fixture_ids
from harness.fixture_runner import run_all_fixtures, run_fixture
from harness.injections import ALL_RULE_IDS


@pytest.mark.parametrize("fixture_id", all_fixture_ids())
def test_fixture_matches_ground_truth(fixture_id: str):
    """Each fixture must produce findings that exactly match ground truth."""
    result = run_fixture(fixture_id)
    assert not result.errors, f"Engine errors: {result.errors}"
    assert result.financial.passed, result.financial.summary()
    assert result.comparison.passed, result.comparison.summary()


@pytest.mark.parametrize("rule_id", ALL_RULE_IDS)
def test_every_rule_has_positive_fixture(rule_id: str):
    """Every rule must have at least one positive fixture in the catalog."""
    positive = [
        spec
        for spec in FIXTURE_CATALOG
        if rule_id in spec.target_rules and spec.fixture_type not in ("negative",)
    ]
    assert positive, f"No positive fixture for rule {rule_id}"


def test_negative_control_passes():
    """Clean company must not trigger any rule."""
    result = run_fixture("27_negative_all_rules")
    assert result.passed, result.comparison.summary()


def test_harness_full_suite():
    """Full harness run must pass with 100% calculation accuracy."""
    harness = run_all_fixtures()
    assert harness.coverage is not None
    assert harness.passed, harness.coverage.to_text()
    assert harness.coverage.false_positives == 0
    assert harness.coverage.false_negatives == 0
    assert harness.coverage.fixtures_passed == harness.coverage.fixtures_total
    assert len(FIXTURE_CATALOG) >= 30
