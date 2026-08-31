"""Compare audit-derived targets to estimator output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from calibration.cases import AuditCalibrationCase
from estimator.modeling.pipeline import run_model


@dataclass
class ComparisonRow:
    case_id: str
    name: str
    audit_target_usd: float
    injected_annual_usd: float
    estimator_central_usd: float
    error_pct: float
    abs_error_pct: float
    audit_vs_injected_pct: float
    matched_findings: int
    expected_findings: int
    source: str


def compare_case(case: AuditCalibrationCase, *, random_seed: int = 42) -> tuple[ComparisonRow, dict[str, Any]]:
    result = run_model(case.answers, random_seed=random_seed, include_sensitivity=False)
    estimator_central = float(result["estimate"]["central"])
    audit_target = case.audit_target_usd
    error_pct = ((estimator_central - audit_target) / audit_target * 100) if audit_target > 0 else 0.0
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
        error_pct=error_pct,
        abs_error_pct=abs(error_pct),
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
) -> tuple[list[ComparisonRow], list[dict[str, Any]]]:
    rows: list[ComparisonRow] = []
    results: list[dict[str, Any]] = []
    for case in cases:
        row, result = compare_case(case, random_seed=random_seed)
        rows.append(row)
        results.append(result)
    return rows, results


def mean_abs_error(rows: list[ComparisonRow]) -> float:
    if not rows:
        return 0.0
    return sum(row.abs_error_pct for row in rows) / len(rows)


def max_abs_error(rows: list[ComparisonRow]) -> float:
    if not rows:
        return 0.0
    return max(row.abs_error_pct for row in rows)


def format_comparison_table(rows: list[ComparisonRow]) -> str:
    lines = [
        f"{'Case':<28} {'Audit':>12} {'Estimator':>12} {'Err%':>8} {'AuditInj':>10}",
        "-" * 74,
    ]
    for row in rows:
        lines.append(
            f"{row.case_id:<28} {row.audit_target_usd:>12,.0f} "
            f"{row.estimator_central_usd:>12,.0f} {row.error_pct:>+7.1f}% "
            f"{row.audit_vs_injected_pct:>+9.1f}%"
        )
    lines.append("-" * 74)
    lines.append(
        f"Mean abs error: {mean_abs_error(rows):.1f}%   Max abs error: {max_abs_error(rows):.1f}%"
    )
    return "\n".join(lines)
