"""Shared date and money utilities for synthetic company generation."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP


def money(value: Decimal | float | int) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def to_decimal(value: str | Decimal | float | int | None) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    cleaned = str(value).strip()
    if not cleaned:
        return None
    if "T" in cleaned:
        return datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(cleaned[:10] if len(cleaned) > 10 else cleaned, fmt).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(cleaned).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def add_months(d: date, months: int = 1) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    days_in_month = [
        31,
        29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ]
    day = min(d.day, days_in_month[month - 1])
    return date(year, month, day)


def add_years(d: date, years: int = 1) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def invoice_schedule(start: date, interval: str, end: date) -> list[date]:
    dates: list[date] = []
    current = start
    while current <= end:
        dates.append(current)
        current = add_months(current) if interval == "monthly" else add_years(current)
    return dates
