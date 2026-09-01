def round_display_amount(value: float) -> float:
    if value <= 0:
        return 0.0
    abs_val = abs(value)
    if abs_val < 10_000:
        step = 500
    elif abs_val < 50_000:
        step = 1_000
    elif abs_val < 100_000:
        step = 5_000
    elif abs_val < 1_000_000:
        step = 10_000
    else:
        step = 50_000
    rounded = round(value / step) * step
    if rounded <= 0:
        return float(step)
    return rounded


def format_currency_range(low: float, high: float) -> str:
    def fmt(v: float) -> str:
        if v >= 1_000_000:
            return f"${v / 1_000_000:.1f}M".replace(".0M", "M")
        if v >= 1_000:
            return f"${v / 1_000:.0f}k"
        return f"${v:,.0f}"

    return f"{fmt(low)} to {fmt(high)}"
