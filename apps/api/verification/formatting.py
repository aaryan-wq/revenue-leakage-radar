from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

DISPLAY_QUANTIZE = Decimal("0.01")


def format_decimal_display(value: str | Decimal | int | float | None) -> str | None:
    if value is None:
        return None
    try:
        normalized = Decimal(str(value)).quantize(DISPLAY_QUANTIZE, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return str(value)
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def normalize_numeric_string(value: Any) -> Any:
    if value is None or not isinstance(value, str):
        return value
    formatted = format_decimal_display(value)
    return formatted if formatted is not None else value


def normalize_evidence_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        row = dict(record)
        for key in ("expected", "actual"):
            if key in row and row[key] is not None:
                row[key] = normalize_numeric_string(str(row[key]))
        normalized.append(row)
    return normalized


def normalize_calculation_trace(trace: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(trace)
    steps = []
    for step in trace.get("steps", []):
        row = dict(step)
        if row.get("value") is not None:
            row["value"] = normalize_numeric_string(str(row["value"]))
        steps.append(row)
    normalized["steps"] = steps
    for key in ("result_monthly", "result_annual"):
        if key in normalized and normalized[key] is not None:
            normalized[key] = normalize_numeric_string(str(normalized[key]))
    return normalized


def normalize_leakage_computation(computation: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(computation)
    for key in ("unit_expected", "unit_actual", "monthly_loss", "annual_loss"):
        if key in normalized and normalized[key] is not None:
            normalized[key] = normalize_numeric_string(str(normalized[key]))
    return normalized
