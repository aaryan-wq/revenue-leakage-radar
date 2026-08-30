"""Sync tests for estimator rule graph parity."""

from __future__ import annotations

from verification.engine.registry import ALL_RULE_MODULES
from verification.findings.generator import RULE_LEAK_FAMILIES

from estimator.modeling.rule_posteriors import get_rule_ids
from estimator.questionnaire.schema import load_hypothesis_rule_map, load_rule_priors


def test_registry_rules_have_rule_priors():
    registry_ids = {module.spec.rule_id for module in ALL_RULE_MODULES}
    registry_ids.add("usage_billing_drift")
    prior_ids = set(get_rule_ids())
    assert registry_ids == prior_ids


def test_hypothesis_map_covers_all_registry_rules():
    registry_ids = {module.spec.rule_id for module in ALL_RULE_MODULES}
    registry_ids.add("usage_billing_drift")
    rule_map = load_hypothesis_rule_map()
    mapped: set[str] = set()
    for meta in rule_map.get("hypotheses", {}).values():
        mapped.update(meta.get("rule_ids", []))
    for meta in rule_map.get("display_rollups", {}).values():
        mapped.update(meta.get("rule_ids", []))
    assert registry_ids == mapped


def test_rule_priors_have_leak_family():
    rule_priors = load_rule_priors()
    for rule_id, cfg in rule_priors.get("rules", {}).items():
        family = cfg.get("leak_family")
        assert family, f"{rule_id} missing leak_family"
        if rule_id in RULE_LEAK_FAMILIES:
            assert cfg["leak_family"] == RULE_LEAK_FAMILIES[rule_id]
