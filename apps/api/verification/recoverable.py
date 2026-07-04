"""Shared recoverable amount logic for headlines and breakdowns."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from verification.types import RuleFinding


def _leakage_semantics(computation: Any) -> str | None:
    if computation is None:
        return None
    semantics = getattr(computation, "semantics", None)
    if semantics is not None:
        return semantics
    if isinstance(computation, dict):
        return computation.get("semantics")
    return None


def _resolve_leakage_computation(finding: RuleFinding | object) -> Any:
    computation = getattr(finding, "leakage_computation", None)
    if computation is not None:
        return computation
    if isinstance(finding, dict):
        computation = finding.get("leakage_computation")
        if computation is not None:
            return computation
    evidence = getattr(finding, "evidence", None)
    if isinstance(finding, dict):
        evidence = finding.get("evidence")
    if isinstance(evidence, str):
        try:
            parsed = json.loads(evidence)
            return parsed.get("leakage_computation")
        except json.JSONDecodeError:
            return None
    if isinstance(evidence, dict):
        return evidence.get("leakage_computation")
    return None


def _monthly_loss_value(finding: RuleFinding | object | dict[str, Any]) -> Decimal:
    if isinstance(finding, dict):
        return Decimal(str(finding.get("estimated_monthly_loss") or 0))
    return Decimal(str(getattr(finding, "estimated_monthly_loss", 0) or 0))


def _annual_loss_value(finding: RuleFinding | object | dict[str, Any]) -> Decimal:
    if isinstance(finding, dict):
        return Decimal(str(finding.get("estimated_arr_loss") or 0))
    return Decimal(str(getattr(finding, "estimated_arr_loss", 0) or 0))


def finding_recoverable_amount(finding: RuleFinding | object) -> Decimal:
    semantics = _leakage_semantics(_resolve_leakage_computation(finding))
    if semantics == "one_time":
        return _monthly_loss_value(finding)
    return _annual_loss_value(finding)


def recoverable_amount_from_payload(payload: dict[str, Any]) -> Decimal:
    """Recoverable amount for serialized finding dicts used in PDF/exports."""
    return finding_recoverable_amount(payload)
