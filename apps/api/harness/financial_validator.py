"""Financial invariant checks on engine findings."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from verification.types import RuleFinding


@dataclass
class FinancialViolation:
    finding_ref: str
    rule_id: str
    kind: str
    message: str


@dataclass
class FinancialValidationResult:
    passed: bool
    violations: list[FinancialViolation] = field(default_factory=list)
    findings_checked: int = 0

    def summary(self) -> str:
        if self.passed:
            return f"Financial validation passed ({self.findings_checked} findings)"
        lines = [f"Financial validation failed ({len(self.violations)} violations)"]
        for violation in self.violations[:10]:
            lines.append(f"  [{violation.kind}] {violation.rule_id}: {violation.message}")
        return "\n".join(lines)


def _annual_matches_monthly(monthly: Decimal, annual: Decimal) -> bool:
    expected = (monthly * Decimal("12")).quantize(Decimal("0.01"))
    actual = annual.quantize(Decimal("0.01"))
    return abs(expected - actual) <= Decimal("0.02")


def validate_findings(findings: list[RuleFinding]) -> FinancialValidationResult:
    violations: list[FinancialViolation] = []
    seen_refs: set[str] = set()

    for finding in findings:
        ref = finding.finding_ref or f"{finding.rule_id}:{finding.customer_id}"
        if ref in seen_refs:
            violations.append(
                FinancialViolation(
                    finding_ref=ref,
                    rule_id=finding.rule_id,
                    kind="duplicate_finding",
                    message=f"Duplicate finding ref {ref}",
                )
            )
        seen_refs.add(ref)

        monthly = finding.estimated_monthly_loss
        annual = finding.estimated_arr_loss

        if monthly < 0 or annual < 0:
            violations.append(
                FinancialViolation(
                    finding_ref=ref,
                    rule_id=finding.rule_id,
                    kind="negative_leakage",
                    message=f"Negative leakage monthly={monthly} annual={annual}",
                )
            )

        if finding.calculation_trace and finding.calculation_trace.semantics == "one_time":
            continue

        if monthly > 0 and annual == 0:
            continue

        if monthly > 0 and not _annual_matches_monthly(monthly, annual):
            violations.append(
                FinancialViolation(
                    finding_ref=ref,
                    rule_id=finding.rule_id,
                    kind="arr_mismatch",
                    message=f"ARR != MRR×12: monthly={monthly} annual={annual} expected={monthly * 12}",
                )
            )

        if finding.expected_value is not None and finding.actual_value is not None:
            if finding.expected_value < 0 or finding.actual_value < 0:
                violations.append(
                    FinancialViolation(
                        finding_ref=ref,
                        rule_id=finding.rule_id,
                        kind="impossible_price",
                        message=f"Negative price expected={finding.expected_value} actual={finding.actual_value}",
                    )
                )

    return FinancialValidationResult(
        passed=len(violations) == 0,
        violations=violations,
        findings_checked=len(findings),
    )
