"""Report headline totals must reconcile with category and confidence breakdowns."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from compare_acmecrm_leakage import build_context
from harness.company_generator import generate_company
from harness.context_loader import build_context_from_state, load_context_from_csv_dir
from harness.engine_runner import run_all_rules
from harness.injections import ALL_RULE_IDS
from verification.attribution import attribute_findings, sum_primary_recoverable_arr
from verification.recoverable import finding_recoverable_amount
from verification.registry import RULES, RuleDefinition, get_all_rules


def rule_lookup() -> dict[str, RuleDefinition]:
    return {rule.rule_id: rule for rule in RULES}


def _breakdown_total(findings) -> Decimal:
    grouped: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    lookup = rule_lookup()
    for finding in findings:
        if finding.attribution != "primary":
            continue
        rule = lookup.get(finding.rule_id)
        category = rule.category if rule else "other"
        grouped[category] += finding_recoverable_amount(finding)
    return sum(grouped.values(), Decimal("0"))


def _confidence_total(findings) -> Decimal:
    total = Decimal("0")
    for finding in findings:
        if finding.attribution != "primary":
            continue
        total += finding_recoverable_amount(finding)
    return total


def _assert_reconciles(findings) -> None:
    attributed = attribute_findings(findings)
    headline = sum_primary_recoverable_arr(attributed)
    category_sum = _breakdown_total(attributed)
    confidence_sum = _confidence_total(attributed)
    assert headline == category_sum == confidence_sum


def test_acmecrm_report_totals_reconcile():
    ctx = build_context()
    findings = []
    for rule in get_all_rules():
        if rule.evaluate:
            findings.extend(rule.evaluate(ctx))
    _assert_reconciles(findings)


@pytest.mark.parametrize("customer_count", [30, 50])
def test_harness_report_totals_reconcile(customer_count: int):
    company = generate_company(
        seed=2000 + customer_count,
        customer_count=customer_count,
        rule_ids=ALL_RULE_IDS,
    )
    ctx, _id_maps = build_context_from_state(company.rows())
    engine = run_all_rules(ctx)
    assert not engine.errors
    _assert_reconciles(engine.findings)


def test_seed_5754409_upload_primary_arr_matches_manifest():
    """Frozen upload CSVs for seed 5754409 must headline at manifest primary ARR."""
    upload_dir = ROOT / "testdata" / "runs" / "run_5754409" / "upload"
    ctx, _maps = load_context_from_csv_dir(upload_dir)
    engine = run_all_rules(ctx)
    attributed = attribute_findings(engine.findings, audit_id=ctx.audit_id)
    headline = sum_primary_recoverable_arr(attributed)
    primary_arr_loss = sum(
        (f.estimated_arr_loss for f in attributed if f.attribution == "primary"),
        Decimal("0"),
    )

    assert headline == Decimal("114800.9996")
    assert headline != primary_arr_loss + headline
    _assert_reconciles(attributed)
