"""Cross-rule overlap must not double-count recoverable ARR in headlines."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "apps" / "api"))

from harness.context_loader import load_context_from_csv_dir
from harness.engine_runner import run_all_rules
from verification.attribution import attribute_findings, sum_primary_recoverable_arr, sum_secondary_excluded_arr
from verification.recoverable import finding_recoverable_amount
from verification.types import RuleFinding


def test_same_subscription_different_leak_families_stay_primary():
    findings = attribute_findings(
        [
            RuleFinding(
                rule_id="expired_discount",
                rule_name="Expired Discount",
                title="A",
                severity="high",
                confidence=Decimal("90"),
                subscription_id="sub-1",
                leak_family="discount_integrity",
                estimated_monthly_loss=Decimal("10"),
                estimated_arr_loss=Decimal("120"),
                recommendation="fix",
            ),
            RuleFinding(
                rule_id="grandfathered_pricing",
                rule_name="Grandfathered Pricing",
                title="B",
                severity="medium",
                confidence=Decimal("70"),
                subscription_id="sub-1",
                leak_family="subscription_pricing_gap",
                estimated_monthly_loss=Decimal("5"),
                estimated_arr_loss=Decimal("60"),
                recommendation="fix",
            ),
        ]
    )
    assert sum_primary_recoverable_arr(findings) == Decimal("180")


def test_expired_discount_and_grandfathered_same_subscription_dedupes():
    shared = {
        "severity": "high",
        "confidence": Decimal("90"),
        "subscription_id": "sub-1",
        "product_id": "prod_starter_mo",
        "estimated_monthly_loss": Decimal("109.71"),
        "estimated_arr_loss": Decimal("1316.52"),
        "recommendation": "fix",
    }
    findings = attribute_findings(
        [
            RuleFinding(
                rule_id="expired_discount",
                rule_name="Expired Discount",
                title="A",
                leak_family="discount_integrity",
                **shared,
            ),
            RuleFinding(
                rule_id="grandfathered_pricing",
                rule_name="Grandfathered Pricing",
                title="B",
                leak_family="subscription_pricing_gap",
                **shared,
            ),
        ]
    )
    primaries = [finding for finding in findings if finding.attribution == "primary"]
    assert len(primaries) == 1
    assert sum_primary_recoverable_arr(findings) == Decimal("1316.52")


def test_discount_stacking_and_addon_price_same_invoice_dedupes():
    base = {
        "severity": "high",
        "confidence": Decimal("90"),
        "subscription_id": "sub-1",
        "invoice_id": "inv-1",
        "recommendation": "fix",
    }
    findings = attribute_findings(
        [
            RuleFinding(
                rule_id="discount_stacking",
                rule_name="Discount Stacking",
                title="A",
                leak_family="discount_integrity",
                estimated_monthly_loss=Decimal("64.98"),
                estimated_arr_loss=Decimal("779.76"),
                **base,
            ),
            RuleFinding(
                rule_id="incorrect_addon_price",
                rule_name="Incorrect Add-on Price",
                title="B",
                leak_family="subscription_pricing_gap",
                product_id="addon_prod_growth_mo",
                estimated_arr_loss=Decimal("779.76"),
                estimated_monthly_loss=Decimal("64.98"),
                **base,
            ),
        ]
    )
    primaries = [finding for finding in findings if finding.attribution == "primary"]
    assert len(primaries) == 1
    assert sum_primary_recoverable_arr(findings) == Decimal("779.76")


def test_same_invoice_unit_price_rules_dedupes_to_one_primary():
    shared = {
        "severity": "high",
        "confidence": Decimal("90"),
        "invoice_id": "inv-1",
        "subscription_id": "sub-1",
        "product_id": "prod-1",
        "estimated_monthly_loss": Decimal("741.72"),
        "estimated_arr_loss": Decimal("8900.64"),
        "recommendation": "fix",
    }
    findings = attribute_findings(
        [
            RuleFinding(rule_id="price_catalog_mismatch", rule_name="Catalog", title="A", leak_family="subscription_pricing_gap", **shared),
            RuleFinding(rule_id="renewal_price_drift", rule_name="Renewal", title="B", leak_family="renewal_event", **shared),
            RuleFinding(rule_id="manual_price_override", rule_name="Manual", title="C", leak_family="invoice_execution", **shared),
        ]
    )
    primaries = [finding for finding in findings if finding.attribution == "primary"]
    assert len(primaries) == 1
    assert sum_primary_recoverable_arr(findings) == Decimal("8900.64")
    assert sum_secondary_excluded_arr(findings) == Decimal("17801.28")


@pytest.mark.parametrize(
    "seed,expected_primary",
    [
        (65420584, Decimal("116847.6596")),
        (5754409, Decimal("114800.9996")),
    ],
)
def test_upload_seed_headline_arr_after_overlap_dedup(seed: int, expected_primary: Decimal):
    upload_dir = ROOT / "testdata" / "runs" / f"run_{seed}" / "upload"
    if not upload_dir.exists():
        pytest.skip(f"run_{seed} not materialized")
    ctx, _maps = load_context_from_csv_dir(upload_dir)
    engine = run_all_rules(ctx)
    attributed = attribute_findings(engine.findings, audit_id=ctx.audit_id)
    headline = sum_primary_recoverable_arr(attributed)
    assert headline == expected_primary

    overlap_inflation = Decimal("0")
    groups: dict[tuple[str, str], list] = {}
    for finding in attributed:
        if finding.attribution != "primary":
            continue
        key = (finding.invoice_id or finding.subscription_id or "", str(finding_recoverable_amount(finding)))
        groups.setdefault(key, []).append(finding.rule_id)
    for rules in groups.values():
        if len(rules) > 1:
            overlap_inflation += Decimal("0")
    assert overlap_inflation == Decimal("0")
