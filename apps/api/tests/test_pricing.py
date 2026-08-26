from decimal import Decimal

from payments.pricing import compute_success_fee_cents, compute_total_amount_usd


def test_compute_success_fee_cents():
    assert compute_success_fee_cents(Decimal("50000")) == 500000
    assert compute_success_fee_cents(Decimal("0")) == 0
    assert compute_success_fee_cents(Decimal("1234.56")) == 12346


def test_compute_total_amount_usd():
    assert compute_total_amount_usd(Decimal("10000")) == 3500.0
    assert compute_total_amount_usd(Decimal("0")) == 2500.0
