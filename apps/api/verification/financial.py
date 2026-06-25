from decimal import Decimal

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


def normalize_interval(interval: str | None) -> str:
    if not interval:
        return "monthly"
    return interval.strip().lower()


def monthly_factor(interval: str | None) -> Decimal:
    return INTERVAL_MONTHLY_FACTORS.get(normalize_interval(interval), Decimal("1"))


def compute_leakage(
    expected: Decimal,
    actual: Decimal,
    quantity: int = 1,
    billing_interval: str | None = "monthly",
) -> tuple[Decimal, Decimal]:
    """Return (monthly_leakage, annual_leakage) from price delta."""
    delta = abs(expected - actual)
    qty = Decimal(str(quantity or 1))
    factor = monthly_factor(billing_interval)
    monthly = (delta * qty * factor).quantize(Decimal("0.0001"))
    annual = (monthly * Decimal("12")).quantize(Decimal("0.0001"))
    return monthly, annual


def weighted_confidence(
    findings: list,
    weight_attr: str = "estimated_arr_loss",
    confidence_attr: str = "confidence",
) -> Decimal | None:
    if not findings:
        return None
    total_weight = Decimal("0")
    weighted_sum = Decimal("0")
    for f in findings:
        weight = Decimal(str(getattr(f, weight_attr, 0) or 0))
        conf = Decimal(str(getattr(f, confidence_attr, 0) or 0))
        if weight > 0:
            weighted_sum += conf * weight
            total_weight += weight
    if total_weight == 0:
        return Decimal(str(getattr(findings[0], confidence_attr, CONFIDENCE_MEDIUM)))
    return (weighted_sum / total_weight).quantize(Decimal("0.01"))
