"""Human-readable finding output for manual dollar verification."""

from __future__ import annotations

from decimal import Decimal

from harness.comparator import ComparisonResult, FindingMismatch
from harness.context_loader import IdMaps
from harness.comparator import _actual_to_external
from verification.types import RuleFinding, RuleExecutionLog


def _fmt_money(value: Decimal | None) -> str:
    if value is None:
        return "-"
    return f"${value:,.2f}"


def format_finding(finding: RuleFinding, id_maps: IdMaps) -> str:
    cust, sub, inv = _actual_to_external(finding, id_maps)
    lines = [
        f"Rule: {finding.rule_id} ({finding.rule_name})",
        f"Customer: {cust or '-'}",
        f"Subscription: {sub or '-'}",
        f"Invoice: {inv or '-'}",
        f"Severity: {finding.severity} | Confidence: {finding.confidence}",
        f"Monthly Leakage: {_fmt_money(finding.estimated_monthly_loss)}",
        f"Annual Leakage: {_fmt_money(finding.estimated_arr_loss)}",
        f"Expected Value: {_fmt_money(finding.expected_value)}",
        f"Actual Value: {_fmt_money(finding.actual_value)}",
        f"Delta: {_fmt_money(finding.delta)}",
        f"Reason Triggered: {finding.title}",
        f"Recommendation: {finding.recommendation}",
    ]

    if finding.evidence:
        lines.append("Evidence:")
        for record in finding.evidence:
            ref = ", ".join(f"{k}={v}" for k, v in record.reference_ids.items())
            lines.append(
                f"  • {record.field}: expected={record.expected} actual={record.actual}"
                + (f" ({ref})" if ref else "")
            )

    if finding.calculation_trace:
        trace = finding.calculation_trace
        lines.append("Calculation Trace:")
        for step in trace.steps:
            lines.append(f"  {step.label}: {step.expression} = {step.result}")
        lines.append(f"  → Monthly: {_fmt_money(trace.result_monthly)} | Annual: {_fmt_money(trace.result_annual)}")
        if trace.semantics:
            lines.append(f"  Semantics: {trace.semantics}")

    return "\n".join(lines)


def format_findings(findings: list[RuleFinding], id_maps: IdMaps) -> str:
    if not findings:
        return "No findings."
    blocks = [format_finding(finding, id_maps) for finding in findings]
    return "\n\n" + ("─" * 60 + "\n\n").join(blocks)


def format_mismatch(mismatch: FindingMismatch, id_maps: IdMaps) -> str:
    lines = [f"[{mismatch.kind}] {mismatch.rule_id}: {mismatch.message}"]
    if mismatch.expected and not mismatch.expected.is_negative:
        lines.append(
            f"  Expected: monthly={mismatch.expected.expected_monthly_leakage} "
            f"annual={mismatch.expected.expected_annual_leakage}"
        )
    if mismatch.actual:
        lines.append(format_finding(mismatch.actual, id_maps))
    return "\n".join(lines)


def format_comparison(comparison: ComparisonResult, id_maps: IdMaps) -> str:
    lines = [comparison.summary()]
    for mismatch in comparison.mismatches:
        lines.append(format_mismatch(mismatch, id_maps))
    return "\n".join(lines)


def format_rule_log(log: RuleExecutionLog) -> str:
    status = log.status
    detail = f"{log.rule_id}: {status}"
    if log.finding_count:
        detail += f" ({log.finding_count} findings)"
    if log.duration_ms:
        detail += f" [{log.duration_ms}ms]"
    if log.skip_reason:
        detail += f", skip: {log.skip_reason}"
    if log.error:
        detail += f", error: {log.error}"
    return detail
