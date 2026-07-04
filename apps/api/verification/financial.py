"""Backward-compatible financial module, delegates to calculator."""

from decimal import Decimal

from verification.calculator.financial import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    INTERVAL_MONTHLY_FACTORS,
    apply_coverage_confidence,
    annualize_period_loss,
    compute_period_leakage,
    compute_recurring_leakage,
    monthly_factor,
    normalize_interval,
    weighted_confidence,
)

def compute_leakage(
    expected: Decimal,
    actual: Decimal,
    quantity: int = 1,
    billing_interval: str | None = "monthly",
) -> tuple[Decimal, Decimal]:
    monthly, annual, _trace = compute_recurring_leakage(expected, actual, quantity, billing_interval)
    return monthly, annual


__all__ = [
    "CONFIDENCE_HIGH",
    "CONFIDENCE_LOW",
    "CONFIDENCE_MEDIUM",
    "INTERVAL_MONTHLY_FACTORS",
    "apply_coverage_confidence",
    "annualize_period_loss",
    "compute_leakage",
    "compute_period_leakage",
    "compute_recurring_leakage",
    "monthly_factor",
    "normalize_interval",
    "weighted_confidence",
]
