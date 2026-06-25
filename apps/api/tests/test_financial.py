from decimal import Decimal

from verification.financial import compute_leakage, monthly_factor, weighted_confidence
from verification.types import RuleFinding


def test_monthly_factor_monthly():
    assert monthly_factor("monthly") == Decimal("1")


def test_monthly_factor_annual():
    assert monthly_factor("annual") == Decimal("1") / Decimal("12")


def test_compute_leakage_monthly():
    monthly, annual = compute_leakage(Decimal("100"), Decimal("80"), 2, "monthly")
    assert monthly == Decimal("40.0000")
    assert annual == Decimal("480.0000")


def test_weighted_confidence():
    findings = [
        RuleFinding(
            rule_id="a",
            title="A",
            severity="high",
            confidence=Decimal("90"),
            estimated_arr_loss=Decimal("1000"),
            recommendation="fix",
        ),
        RuleFinding(
            rule_id="b",
            title="B",
            severity="low",
            confidence=Decimal("50"),
            estimated_arr_loss=Decimal("1000"),
            recommendation="fix",
        ),
    ]
    result = weighted_confidence(findings)
    assert result == Decimal("70.00")
