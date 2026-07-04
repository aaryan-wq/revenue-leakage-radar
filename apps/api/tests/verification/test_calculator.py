from decimal import Decimal

from verification.calculator.financial import (
    annualize_period_loss,
    compute_recurring_leakage,
    price_delta,
    seat_delta,
)
from verification.eligibility.engine import resolve_eligibility
from verification.engine.registry import get_rule_module


def test_price_delta_absolute():
    assert price_delta(Decimal("100"), Decimal("80")) == Decimal("20.0000")


def test_compute_recurring_leakage_trace():
    monthly, annual, trace = compute_recurring_leakage(Decimal("100"), Decimal("80"), 2, "monthly")
    assert monthly == Decimal("40.0000")
    assert annual == Decimal("480.0000")
    assert trace.result_monthly == monthly
    assert len(trace.steps) >= 5


def test_seat_delta_trace():
    monthly, annual, trace = seat_delta(10, 7, Decimal("50"), "monthly")
    assert monthly == Decimal("150.0000")
    assert annual == Decimal("1800.0000")
    assert trace.steps[0].step_id == "expected_seats"


def test_annualize_period_loss_quarterly():
    monthly, annual = annualize_period_loss(Decimal("300"), "quarterly")
    assert monthly == Decimal("100.0000")
    assert annual == Decimal("1200.0000")


def test_eligibility_skips_without_required_fields():
    from verification.context import CanonicalContext
    from core.enums import DataTier

    ctx = CanonicalContext(
        audit_id=__import__("uuid").uuid4(),
        company_id=__import__("uuid").uuid4(),
        data_tier=DataTier.INSUFFICIENT,
    )
    module = get_rule_module("legacy_pricing")
    assert module is not None
    result = resolve_eligibility(module.spec, ctx)
    assert result.status == "skipped"
