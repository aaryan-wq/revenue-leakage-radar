"""Compare audit-derived targets to estimator output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from calibration.cases import AuditCalibrationCase
from estimator.modeling.pipeline import run_model

MIN_AUDIT_USD_FOR_PCT_ERROR = 500.0


@dataclass
class ComparisonRow:
    case_id: str
    name: str
    audit_target_usd: float
    injected_annual_usd: float
    estimator_central_usd: float
    estimator_rule_usd: float
    primary_rule_id: str
    error_pct: float
    rule_error_pct: float
    abs_error_pct: float
    abs_rule_error_pct: float
    audit_vs_injected_pct: float
    matched_findings: int
    expected_findings: int
    source: str


def _rule_expected(result: dict[str, Any], rule_id: str) -> float:
    for row in result.get("rule_breakdown", []):
        if row.get("rule_id") == rule_id:
            return float(row.get("expected", 0))
    return 0.0


def _pct_error(estimate: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return (estimate - target) / target * 100


def compare_case(case: AuditCalibrationCase, *, random_seed: int = 42) -> tuple[ComparisonRow, dict[str, Any]]:
    result = run_model(case.answers, random_seed=random_seed, include_sensitivity=False)
    estimator_central = float(result["estimate"]["central"])
    audit_target = case.audit_target_usd
    primary_rule = case.injected_rules[0] if len(case.injected_rules) == 1 else ""
    estimator_rule = _rule_expected(result, primary_rule) if primary_rule else estimator_central
    injected = case.injected_annual_usd
    audit_vs_injected = (
        ((audit_target - injected) / injected * 100) if injected > 0 else 0.0
    )
    row = ComparisonRow(
        case_id=case.case_id,
        name=case.name,
        audit_target_usd=audit_target,
        injected_annual_usd=injected,
        estimator_central_usd=estimator_central,
        estimator_rule_usd=estimator_rule,
        primary_rule_id=primary_rule,
        error_pct=_pct_error(estimator_central, audit_target),
        rule_error_pct=_pct_error(estimator_rule, audit_target),
        abs_error_pct=abs(_pct_error(estimator_central, audit_target)),
        abs_rule_error_pct=abs(_pct_error(estimator_rule, audit_target)),
        audit_vs_injected_pct=audit_vs_injected,
        matched_findings=case.audit.matched_findings,
        expected_findings=case.audit.expected_findings,
        source=case.source,
    )
    return row, result


def compare_cases(
    cases: list[AuditCalibrationCase],
    *,
    random_seed: int = 42,
    overlay_multipliers: dict[str, float] | None = None,
) -> tuple[list[ComparisonRow], list[dict[str, Any]]]:
    if not overlay_multipliers:
        rows: list[ComparisonRow] = []
        results: list[dict[str, Any]] = []
        for case in cases:
            row, result = compare_case(case, random_seed=random_seed)
            rows.append(row)
            results.append(result)
        return rows, results

    from calibration.tune import _restore_overlay_patch, _with_overlay_multipliers

    schema, pipeline, rule_posteriors, original = _with_overlay_multipliers(overlay_multipliers)
    try:
        rows: list[ComparisonRow] = []
        results: list[dict[str, Any]] = []
        for case in cases:
            row, result = compare_case(case, random_seed=random_seed)
            rows.append(row)
            results.append(result)
        return rows, results
    finally:
        _restore_overlay_patch(schema, pipeline, rule_posteriors, original)


def mean_abs_error(rows: list[ComparisonRow], *, use_rule_level: bool = True) -> float:
    if not rows:
        return 0.0
    total = 0.0
    count = 0
    for row in rows:
        if row.audit_target_usd < MIN_AUDIT_USD_FOR_PCT_ERROR:
            continue
        total += row.abs_rule_error_pct if use_rule_level and row.primary_rule_id else row.abs_error_pct
        count += 1
    if count == 0:
        return sum(row.abs_rule_error_pct if use_rule_level else row.abs_error_pct for row in rows) / len(rows)
    return total / count


def max_abs_error(rows: list[ComparisonRow], *, use_rule_level: bool = True) -> float:
    if not rows:
        return 0.0
    values = [
        row.abs_rule_error_pct if use_rule_level and row.primary_rule_id else row.abs_error_pct
        for row in rows
        if row.audit_target_usd >= MIN_AUDIT_USD_FOR_PCT_ERROR or row.audit_target_usd > 0
    ]
    return max(values) if values else 0.0


def format_comparison_table(rows: list[ComparisonRow], *, use_rule_level: bool = True) -> str:
    metric_label = "RuleErr" if use_rule_level else "Err"
    lines = [
        f"{'Case':<28} {'Audit':>10} {'EstRule':>10} {'Central':>10} {metric_label:>8} {'AuditInj':>9}",
        "-" * 80,
    ]
    for row in rows:
        err = row.rule_error_pct if use_rule_level and row.primary_rule_id else row.error_pct
        lines.append(
            f"{row.case_id:<28} {row.audit_target_usd:>10,.0f} "
            f"{row.estimator_rule_usd:>10,.0f} {row.estimator_central_usd:>10,.0f} "
            f"{err:>+7.1f}% {row.audit_vs_injected_pct:>+8.1f}%"
        )
    lines.append("-" * 80)
    lines.append(
        f"Mean abs error (rule-level, audit >= ${MIN_AUDIT_USD_FOR_PCT_ERROR:,.0f}): "
        f"{mean_abs_error(rows, use_rule_level=use_rule_level):.1f}%   "
        f"Max: {max_abs_error(rows, use_rule_level=use_rule_level):.1f}%"
    )
    return "\n".join(lines)
