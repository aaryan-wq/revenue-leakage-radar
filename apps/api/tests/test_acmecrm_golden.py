"""AcmeCRM golden-file assertions for primary recoverable ARR."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from compare_acmecrm_leakage import build_context
from verification.attribution import attribute_findings, sum_primary_recoverable_arr
from verification.registry import get_all_rules

EXPECTED_PATH = ROOT / "testdata" / "acmecrm" / "expected.json"
MANIFEST_PATH = ROOT / "testdata" / "acmecrm" / "manifest.json"


@pytest.fixture(scope="module")
def acmecrm_expected() -> dict:
    return json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def acmecrm_attributed():
    ctx = build_context()
    findings = []
    for rule in get_all_rules():
        if rule.evaluate:
            findings.extend(rule.evaluate(ctx))
    return attribute_findings(findings), ctx


def test_acmecrm_portfolio_primary_arr_within_bounds(acmecrm_expected, acmecrm_attributed):
    attributed, _ctx = acmecrm_attributed
    portfolio = acmecrm_expected["portfolio"]
    primary = sum_primary_recoverable_arr(attributed)
    assert primary >= Decimal(portfolio["primary_recoverable_arr_min"])
    assert primary <= Decimal(portfolio["primary_recoverable_arr_max"])
    assert len(attributed) <= portfolio["max_finding_count"]


def test_acmecrm_scenarios_detect_injected_subscriptions(acmecrm_expected, acmecrm_attributed):
    attributed, ctx = acmecrm_attributed
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    for scenario_name, bounds in acmecrm_expected["scenarios"].items():
        external_sub_ids = set(bounds["subscription_ids"])
        detected_subs = set()
        scenario_primary = Decimal("0")
        for finding in attributed:
            if finding.attribution != "primary":
                continue
            if not finding.subscription_id:
                continue
            ext_sub = next(
                (
                    sub.external_subscription_id
                    for sub in ctx.subscriptions
                    if str(sub.id) == str(finding.subscription_id)
                ),
                None,
            )
            if ext_sub in external_sub_ids:
                detected_subs.add(ext_sub)
                scenario_primary += finding.estimated_arr_loss

        manifest_subs = set(
            manifest["injected_scenarios"][scenario_name]["subscription_ids"]
        )
        assert manifest_subs.issubset(detected_subs), (
            f"{scenario_name}: missing subscriptions {manifest_subs - detected_subs}"
        )
        assert scenario_primary >= Decimal(bounds["primary_arr_min"])
        assert scenario_primary <= Decimal(bounds["primary_arr_max"])
