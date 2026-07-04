"""Coverage and accuracy metrics for the verification harness."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from harness.comparator import ComparisonResult, FindingMismatch
from harness.financial_validator import FinancialValidationResult
from harness.fixture_catalog import FIXTURE_CATALOG
from harness.injections import ALL_RULE_IDS
from verification.types import RuleExecutionLog


@dataclass
class RuleCoverage:
    rule_id: str
    positive_fixtures: int = 0
    negative_fixtures: int = 0
    passed: bool = True
    false_positives: int = 0
    false_negatives: int = 0
    skipped: bool = False


@dataclass
class FixtureResult:
    fixture_id: str
    passed: bool
    comparison: ComparisonResult
    financial: FinancialValidationResult
    duration_ms: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class HarnessCoverageReport:
    fixtures_total: int
    fixtures_passed: int
    rules_tested: int
    rules_passed: int
    rules_failed: int
    coverage_percent: Decimal
    calculation_accuracy_percent: Decimal
    false_positives: int
    false_negatives: int
    skipped_rules: list[str]
    total_duration_ms: int
    rule_coverage: dict[str, RuleCoverage]
    fixture_results: list[FixtureResult]
    engine_errors: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        lines = [
            "=" * 60,
            "VERIFICATION ENGINE HARNESS, COVERAGE REPORT",
            "=" * 60,
            "",
            f"Fixtures Run:          {self.fixtures_passed}/{self.fixtures_total}",
            f"Rules Tested:          {self.rules_tested}",
            f"Rules Passed:          {self.rules_passed}",
            f"Rules Failed:          {self.rules_failed}",
            f"Coverage:              {self.coverage_percent:.1f}%",
            f"Calculation Accuracy:  {self.calculation_accuracy_percent:.1f}%",
            f"False Positives:       {self.false_positives}",
            f"False Negatives:       {self.false_negatives}",
            f"Skipped Rules:         {len(self.skipped_rules)}",
            f"Performance:           {self.total_duration_ms:,} ms total",
            "",
        ]

        if self.skipped_rules:
            lines.append("Skipped Rules:")
            for rule_id in self.skipped_rules:
                lines.append(f"  • {rule_id}")
            lines.append("")

        failed_fixtures = [result for result in self.fixture_results if not result.passed]
        if failed_fixtures:
            lines.append("Failed Fixtures:")
            for result in failed_fixtures:
                lines.append(f"  FAIL {result.fixture_id}: {result.comparison.summary()}")
            lines.append("")

        failed_rules = [rule_id for rule_id, cov in self.rule_coverage.items() if not cov.passed]
        if failed_rules:
            lines.append("Failed Rules:")
            for rule_id in sorted(failed_rules):
                cov = self.rule_coverage[rule_id]
                lines.append(
                    f"  FAIL {rule_id}: FP={cov.false_positives} FN={cov.false_negatives}"
                )
            lines.append("")

        lines.append("Rule Coverage Detail:")
        for rule_id in ALL_RULE_IDS:
            cov = self.rule_coverage.get(rule_id, RuleCoverage(rule_id=rule_id))
            status = "PASS" if cov.passed else "FAIL"
            lines.append(
                f"  {status} {rule_id}: +{cov.positive_fixtures} pos, +{cov.negative_fixtures} neg"
            )

        if self.engine_errors:
            lines.append("")
            lines.append("Engine Errors:")
            for error in self.engine_errors:
                lines.append(f"  • {error}")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


def _count_mismatch_kinds(mismatches: list[FindingMismatch]) -> tuple[int, int]:
    false_positives = sum(1 for mismatch in mismatches if mismatch.kind == "false_positive")
    false_negatives = sum(
        1 for mismatch in mismatches if mismatch.kind in ("missing", "monthly_mismatch", "annual_mismatch")
    )
    return false_positives, false_negatives


def build_coverage_report(
    fixture_results: list[FixtureResult],
    all_logs: list[RuleExecutionLog],
) -> HarnessCoverageReport:
    rule_coverage: dict[str, RuleCoverage] = {rule_id: RuleCoverage(rule_id=rule_id) for rule_id in ALL_RULE_IDS}

    total_fp = 0
    total_fn = 0
    total_expected = 0
    total_matched = 0
    fixtures_passed = 0
    total_duration = 0
    engine_errors: list[str] = []

    for result in fixture_results:
        total_duration += result.duration_ms
        engine_errors.extend(result.errors)

        if result.passed:
            fixtures_passed += 1

        fp, fn = _count_mismatch_kinds(result.comparison.mismatches)
        total_fp += fp
        total_fn += fn
        total_expected += result.comparison.expected_count
        total_matched += result.comparison.matched

        spec_rules = set()
        from harness.fixture_catalog import get_fixture_spec

        spec = get_fixture_spec(result.fixture_id)
        if spec:
            spec_rules = set(spec.target_rules)

        for rule_id in spec_rules:
            cov = rule_coverage[rule_id]
            if spec and spec.fixture_type == "negative":
                cov.negative_fixtures += 1
            else:
                cov.positive_fixtures += 1
            if fp or fn or not result.passed:
                cov.false_positives += fp
                cov.false_negatives += fn
                cov.passed = False

    skipped_rules = sorted(
        log.rule_id for log in all_logs if log.status == "skipped" and log.rule_id not in {
            rule_id for rule_id, cov in rule_coverage.items() if cov.positive_fixtures > 0
        }
    )

    rules_tested = sum(1 for cov in rule_coverage.values() if cov.positive_fixtures or cov.negative_fixtures)
    rules_passed = sum(1 for cov in rule_coverage.values() if cov.passed and (cov.positive_fixtures or cov.negative_fixtures))
    rules_failed = rules_tested - rules_passed

    coverage_pct = (Decimal(rules_passed) / Decimal(len(ALL_RULE_IDS)) * 100) if ALL_RULE_IDS else Decimal("100")
    accuracy_pct = (
        (Decimal(total_matched) / Decimal(total_expected) * 100) if total_expected else Decimal("100")
    )

    return HarnessCoverageReport(
        fixtures_total=len(fixture_results),
        fixtures_passed=fixtures_passed,
        rules_tested=rules_tested,
        rules_passed=rules_passed,
        rules_failed=rules_failed,
        coverage_percent=coverage_pct.quantize(Decimal("0.1")),
        calculation_accuracy_percent=accuracy_pct.quantize(Decimal("0.1")),
        false_positives=total_fp,
        false_negatives=total_fn,
        skipped_rules=skipped_rules,
        total_duration_ms=total_duration,
        rule_coverage=rule_coverage,
        fixture_results=fixture_results,
        engine_errors=engine_errors,
    )
