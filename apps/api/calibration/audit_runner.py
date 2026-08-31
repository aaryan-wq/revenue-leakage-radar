"""Run the verification engine on harness CSV rows."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from harness.comparator import compare_findings
from harness.context_loader import build_context_from_state
from harness.engine_runner import run_all_rules
from harness.types import GroundTruthFinding
from verification.attribution import attribute_findings, sum_primary_recoverable_arr


@dataclass
class AuditResult:
    primary_recoverable_arr: float
    injected_annual_leakage: float
    ground_truth_annual: float
    per_rule_arr: dict[str, float] = field(default_factory=dict)
    matched_findings: int = 0
    expected_findings: int = 0
    passed: bool = False


def _sum_annual(findings: list[GroundTruthFinding]) -> Decimal:
    return sum(
        (f.expected_annual_leakage for f in findings if not f.is_negative),
        Decimal("0"),
    )


def _per_rule_from_attributed(attributed: list) -> dict[str, float]:
    totals: dict[str, Decimal] = {}
    for finding in attributed:
        is_primary = getattr(finding, "is_primary", None)
        if is_primary is False:
            continue
        rule_id = getattr(finding, "rule_id", None)
        amount = getattr(finding, "estimated_arr_loss", None)
        if not rule_id or amount is None:
            continue
        totals[str(rule_id)] = totals.get(str(rule_id), Decimal("0")) + Decimal(str(amount))
    return {rule_id: float(value) for rule_id, value in totals.items()}


def run_audit_on_rows(
    rows: dict[str, list[dict]],
    ground_truth: list[GroundTruthFinding],
) -> AuditResult:
    positives = [finding for finding in ground_truth if not finding.is_negative]
    ctx, maps = build_context_from_state(rows)
    engine_result = run_all_rules(ctx)
    comparison = compare_findings(positives, engine_result.findings, maps, allow_extra=True)
    attributed = attribute_findings(engine_result.findings, audit_id=ctx.audit_id)
    primary = sum_primary_recoverable_arr(attributed)
    injected_annual = _sum_annual(positives)
    return AuditResult(
        primary_recoverable_arr=float(primary),
        injected_annual_leakage=float(injected_annual),
        ground_truth_annual=float(injected_annual),
        per_rule_arr=_per_rule_from_attributed(attributed),
        matched_findings=comparison.matched,
        expected_findings=comparison.expected_count,
        passed=comparison.passed,
    )
