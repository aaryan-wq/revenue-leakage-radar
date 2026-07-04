from __future__ import annotations

import logging
import time
from decimal import Decimal

from verification.attribution import attribute_findings
from verification.calculator.financial import apply_coverage_confidence, weighted_confidence
from verification.context import CanonicalContext
from verification.eligibility.engine import resolve_eligibility
from verification.engine.registry import get_all_rules
from verification.findings.generator import FindingGenerator
from verification.rules.protocol import RuleModule
from verification.types import RuleExecutionLog, RuleFinding, ScanReport

logger = logging.getLogger(__name__)


def _downgrade_findings(findings: list[RuleFinding]) -> list[RuleFinding]:
    return [
        finding.model_copy(
            update={"confidence": apply_coverage_confidence(finding.confidence, is_partial=True)}
        )
        for finding in findings
    ]


def run_engine(ctx: CanonicalContext, *, rules: list[RuleModule] | None = None) -> tuple[list[RuleFinding], ScanReport]:
    rule_modules = rules or get_all_rules()
    all_findings: list[RuleFinding] = []
    rule_logs: list[RuleExecutionLog] = []
    rules_ran = 0
    rules_skipped = 0
    rules_partial = 0
    rules_errored = 0

    for module in rule_modules:
        spec = module.spec
        start = time.perf_counter()
        eligibility = resolve_eligibility(spec, ctx)

        if eligibility.status == "skipped":
            rules_skipped += 1
            rule_logs.append(
                RuleExecutionLog(
                    rule_id=spec.rule_id,
                    status="skipped",
                    skip_reason=eligibility.skip_reason,
                    duration_ms=int((time.perf_counter() - start) * 1000),
                )
            )
            continue

        status = "partial" if eligibility.status == "partial" else "ran"
        coverage_note = eligibility.skip_reason if status == "partial" else None

        try:
            results = module.evaluate(ctx)
            findings = [
                FindingGenerator.from_rule_result(spec, result, audit_id=ctx.audit_id)
                for result in results
            ]
            if status == "partial":
                findings = _downgrade_findings(findings)
                rules_partial += 1
            else:
                rules_ran += 1
            all_findings.extend(findings)
            rule_logs.append(
                RuleExecutionLog(
                    rule_id=spec.rule_id,
                    status=status,
                    finding_count=len(findings),
                    coverage_note=coverage_note,
                    duration_ms=int((time.perf_counter() - start) * 1000),
                )
            )
        except Exception as exc:
            logger.exception("Rule %s failed", spec.rule_id)
            rules_errored += 1
            rule_logs.append(
                RuleExecutionLog(
                    rule_id=spec.rule_id,
                    status="error",
                    error=str(exc),
                    duration_ms=int((time.perf_counter() - start) * 1000),
                )
            )

    attributed = attribute_findings(all_findings, audit_id=ctx.audit_id)
    primary = [finding for finding in attributed if finding.attribution == "primary"]
    overall_conf = weighted_confidence(primary)

    report = ScanReport(
        rules_total=len(rule_modules),
        rules_completed=rules_ran + rules_partial,
        rules_skipped=rules_skipped,
        rules_partial=rules_partial,
        rules_errored=rules_errored,
        finding_count=len(attributed),
        recoverable_arr=str(sum_primary_recoverable_arr(attributed)),
        overall_confidence=str(overall_conf) if overall_conf is not None else None,
        data_tier=ctx.data_tier.value,
        rule_logs=rule_logs,
    )
    return attributed, report


def sum_primary_recoverable_arr(findings: list[RuleFinding]) -> Decimal:
    from verification.recoverable import finding_recoverable_amount

    total = Decimal("0")
    for finding in findings:
        if finding.attribution != "primary":
            continue
        total += finding_recoverable_amount(finding)
    return total.quantize(Decimal("0.0001"))
