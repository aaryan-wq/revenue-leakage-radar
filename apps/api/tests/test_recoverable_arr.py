from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from compare_acmecrm_leakage import build_context
from verification.attribution import attribute_findings, sum_primary_recoverable_arr
from verification.registry import get_all_rules
from verification.types import RuleFinding


def test_aggregate_recoverable_arr_sums_primary_per_family():
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
            RuleFinding(
                rule_id="invoice_price_mismatch",
                rule_name="Invoice Price Mismatch",
                title="C",
                severity="medium",
                confidence=Decimal("90"),
                subscription_id="sub-2",
                leak_family="invoice_execution",
                estimated_monthly_loss=Decimal("8"),
                estimated_arr_loss=Decimal("96"),
                recommendation="fix",
            ),
        ]
    )

    assert sum_primary_recoverable_arr(findings) == Decimal("276")


def test_acmecrm_primary_recoverable_arr_is_reasonable():
    ctx = build_context()
    findings: list[RuleFinding] = []
    for rule in get_all_rules():
        if rule.evaluate:
            findings.extend(rule.evaluate(ctx))

    attributed = attribute_findings(findings)
    recoverable = sum_primary_recoverable_arr(attributed)
    assert recoverable > Decimal("2500000")
    assert recoverable < Decimal("6000000")
