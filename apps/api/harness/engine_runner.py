"""Run verification rules against a CanonicalContext."""

from __future__ import annotations

from dataclasses import dataclass, field

from verification.context import CanonicalContext
from verification.engine.registry import get_rule_module
from verification.engine.runner import run_engine
from verification.types import RuleExecutionLog, RuleFinding


@dataclass
class EngineRunResult:
    findings: list[RuleFinding] = field(default_factory=list)
    logs: list[RuleExecutionLog] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def run_all_rules(
    ctx: CanonicalContext,
    *,
    rule_ids: list[str] | None = None,
) -> EngineRunResult:
    modules = None
    if rule_ids is not None:
        modules = [module for rule_id in rule_ids if (module := get_rule_module(rule_id)) is not None]
    findings, report = run_engine(ctx, rules=modules)
    errors = [log.error for log in report.rule_logs if log.error]
    return EngineRunResult(findings=findings, logs=report.rule_logs, errors=[error for error in errors if error])
