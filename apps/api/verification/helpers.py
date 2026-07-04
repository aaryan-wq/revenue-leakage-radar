"""Shared helpers used by reports and legacy imports."""

from decimal import Decimal

from verification.attribution import sum_primary_recoverable_arr
from verification.calculator.financial import annualize_period_loss
from verification.types import RuleFinding

aggregate_recoverable_arr = sum_primary_recoverable_arr

__all__ = ["aggregate_recoverable_arr", "annualize_period_loss"]
