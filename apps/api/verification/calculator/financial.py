"""Single source of truth for all monetary calculations in the verification engine."""

from __future__ import annotations

from decimal import Decimal

from verification.calculator.trace import CalculationTrace, TraceBuilder

CONFIDENCE_HIGH = Decimal("90")
CONFIDENCE_MEDIUM = Decimal("70")
CONFIDENCE_LOW = Decimal("50")

INTERVAL_MONTHLY_FACTORS: dict[str, Decimal] = {
    "monthly": Decimal("1"),
    "month": Decimal("1"),
    "m": Decimal("1"),
    "quarterly": Decimal("1") / Decimal("3"),
    "quarter": Decimal("1") / Decimal("3"),
    "q": Decimal("1") / Decimal("3"),
    "annual": Decimal("1") / Decimal("12"),
    "yearly": Decimal("1") / Decimal("12"),
    "year": Decimal("1") / Decimal("12"),
    "annualy": Decimal("1") / Decimal("12"),
}


class InsufficientDataError(ValueError):
    """Raised when a required financial input is missing."""


def _require(value: Decimal | int | None, name: str) -> Decimal:
    if value is None:
        raise InsufficientDataError(f"Missing required value: {name}")
    return Decimal(str(value))


def normalize_interval(interval: str | None) -> str:
    if not interval:
        return "monthly"
    return interval.strip().lower()


def monthly_factor(interval: str | None) -> Decimal:
    return INTERVAL_MONTHLY_FACTORS.get(normalize_interval(interval), Decimal("1"))


def price_delta(expected: Decimal, actual: Decimal) -> Decimal:
    return abs(_require(expected, "expected") - _require(actual, "actual")).quantize(Decimal("0.0001"))


def mrr(unit_price: Decimal, quantity: int, interval: str | None) -> Decimal:
    price = _require(unit_price, "unit_price")
    qty = Decimal(str(quantity or 1))
    factor = monthly_factor(interval)
    return (price * qty * factor).quantize(Decimal("0.0001"))


def arr(monthly: Decimal) -> Decimal:
    return (_require(monthly, "monthly") * Decimal("12")).quantize(Decimal("0.0001"))


def seat_delta(
    expected_seats: int,
    actual_seats: int,
    unit_price: Decimal,
    interval: str | None,
) -> tuple[Decimal, Decimal, CalculationTrace]:
    seat_diff = max(0, _require(expected_seats, "expected_seats") - _require(actual_seats, "actual_seats"))
    price = _require(unit_price, "unit_price")
    factor = monthly_factor(interval)
    monthly = (Decimal(str(seat_diff)) * price * factor).quantize(Decimal("0.0001"))
    annual = arr(monthly)
    trace = (
        TraceBuilder()
        .add("expected_seats", "Expected seats", Decimal(str(expected_seats)))
        .add("actual_seats", "Actual seats", Decimal(str(actual_seats)))
        .add("seat_difference", "Seat difference", Decimal(str(seat_diff)))
        .add("unit_price", "Unit price", price)
        .add("interval_factor", "Interval factor", factor)
        .add("monthly_leakage", "Monthly leakage", monthly)
        .add("annual_leakage", "Annual leakage", annual)
        .finish(monthly, annual)
    )
    return monthly, annual, trace


def discount_amount(discount_type: str, discount_value: Decimal, base: Decimal) -> Decimal:
    base_amount = _require(base, "base")
    value = _require(discount_value, "discount_value")
    dtype = (discount_type or "percent").lower()
    if dtype in ("percent", "percentage", "%"):
        return (base_amount * value / Decimal("100")).quantize(Decimal("0.0001"))
    return value.quantize(Decimal("0.0001"))


def percentage_discount(base: Decimal, pct: Decimal) -> Decimal:
    return discount_amount("percent", pct, base)


def renewal_increase(expected: Decimal, actual: Decimal, interval: str | None) -> tuple[Decimal, Decimal, CalculationTrace]:
    return compute_recurring_leakage(expected, actual, 1, interval, semantics="renewal_increase")


def invoice_difference(expected: Decimal, actual: Decimal, interval: str | None) -> tuple[Decimal, Decimal, CalculationTrace]:
    return compute_recurring_leakage(expected, actual, 1, interval, semantics="invoice_difference")


def annualize_period_loss(
    period_amount: Decimal,
    billing_interval: str | None,
) -> tuple[Decimal, Decimal]:
    amount = _require(period_amount, "period_amount")
    factor = monthly_factor(billing_interval)
    monthly = (amount * factor).quantize(Decimal("0.0001"))
    annual = arr(monthly)
    return monthly, annual


def compute_recurring_leakage(
    expected: Decimal,
    actual: Decimal,
    quantity: int = 1,
    billing_interval: str | None = "monthly",
    *,
    semantics: str = "recurring_run_rate",
    source_refs: dict[str, str] | None = None,
) -> tuple[Decimal, Decimal, CalculationTrace]:
    unit_expected = _require(expected, "expected")
    unit_actual = _require(actual, "actual")
    qty = quantity or 1
    delta = price_delta(unit_expected, unit_actual)
    factor = monthly_factor(billing_interval)
    monthly = (delta * Decimal(str(qty)) * factor).quantize(Decimal("0.0001"))
    annual_val = arr(monthly)
    refs = source_refs or {}
    trace = (
        TraceBuilder(semantics=semantics)
        .add("expected_value", "Expected value", unit_expected, source_refs=refs)
        .add("actual_value", "Actual value", unit_actual, source_refs=refs)
        .add("difference", "Difference", delta, source_refs=refs)
        .add("quantity", "Quantity", Decimal(str(qty)), source_refs=refs)
        .add("interval_factor", "Interval factor", factor, source_refs=refs)
        .add("monthly_leakage", "Monthly leakage", monthly, source_refs=refs)
        .add("annual_leakage", "Annual leakage", annual_val, source_refs=refs)
        .finish(monthly, annual_val)
    )
    return monthly, annual_val, trace


def compute_period_leakage(
    period_expected: Decimal,
    period_actual: Decimal,
    billing_interval: str | None,
    *,
    source_refs: dict[str, str] | None = None,
) -> tuple[Decimal, Decimal, CalculationTrace]:
    expected = _require(period_expected, "period_expected")
    actual = _require(period_actual, "period_actual")
    period_loss = price_delta(expected, actual)
    monthly, annual_val = annualize_period_loss(period_loss, billing_interval)
    refs = source_refs or {}
    trace = (
        TraceBuilder(semantics="per_period")
        .add("period_expected", "Period expected", expected, source_refs=refs)
        .add("period_actual", "Period actual", actual, source_refs=refs)
        .add("period_difference", "Period difference", period_loss, source_refs=refs)
        .add("interval_factor", "Interval factor", monthly_factor(billing_interval), source_refs=refs)
        .add("monthly_leakage", "Monthly leakage", monthly, source_refs=refs)
        .add("annual_leakage", "Annual leakage", annual_val, source_refs=refs)
        .finish(monthly, annual_val)
    )
    return monthly, annual_val, trace


def compute_zero_leakage(*, semantics: str = "operational") -> CalculationTrace:
    return TraceBuilder(semantics=semantics).finish(Decimal("0"), Decimal("0"))


def weighted_confidence(
    findings: list,
    weight_attr: str = "estimated_arr_loss",
    confidence_attr: str = "confidence",
) -> Decimal | None:
    if not findings:
        return None
    total_weight = Decimal("0")
    weighted_sum = Decimal("0")
    for finding in findings:
        weight = Decimal(str(getattr(finding, weight_attr, 0) or 0))
        conf = Decimal(str(getattr(finding, confidence_attr, 0) or 0))
        if weight > 0:
            weighted_sum += conf * weight
            total_weight += weight
    if total_weight == 0:
        return Decimal(str(getattr(findings[0], confidence_attr, CONFIDENCE_MEDIUM)))
    return (weighted_sum / total_weight).quantize(Decimal("0.01"))


def apply_coverage_confidence(base: Decimal, is_partial: bool) -> Decimal:
    if not is_partial:
        return base
    if base >= CONFIDENCE_HIGH:
        return CONFIDENCE_MEDIUM
    if base >= CONFIDENCE_MEDIUM:
        return CONFIDENCE_LOW
    return base


class FinancialCalculator:
    """Namespace wrapper for calculator functions used by rules."""

    price_delta = staticmethod(price_delta)
    mrr = staticmethod(mrr)
    arr = staticmethod(arr)
    seat_delta = staticmethod(seat_delta)
    discount_amount = staticmethod(discount_amount)
    percentage_discount = staticmethod(percentage_discount)
    renewal_increase = staticmethod(renewal_increase)
    invoice_difference = staticmethod(invoice_difference)
    compute_recurring_leakage = staticmethod(compute_recurring_leakage)
    compute_period_leakage = staticmethod(compute_period_leakage)
    compute_zero_leakage = staticmethod(compute_zero_leakage)
    annualize_period_loss = staticmethod(annualize_period_loss)
