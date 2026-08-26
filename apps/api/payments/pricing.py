from decimal import Decimal, ROUND_HALF_UP

BASE_FEE_USD = Decimal("2500")
SUCCESS_FEE_RATE = Decimal("0.10")


def compute_success_fee_cents(confirmed_recovery_usd: Decimal) -> int:
    fee = (confirmed_recovery_usd * SUCCESS_FEE_RATE * Decimal("100")).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    return int(fee)


def compute_total_amount_usd(confirmed_recovery_usd: Decimal) -> float:
    return float(BASE_FEE_USD + confirmed_recovery_usd * SUCCESS_FEE_RATE)
