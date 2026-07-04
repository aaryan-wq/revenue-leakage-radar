"""Execute verification fixtures and validate against ground truth."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from harness.comparator import compare_findings
from harness.context_loader import build_context_from_state
from harness.coverage_report import FixtureResult, HarnessCoverageReport, build_coverage_report
from harness.engine_runner import run_all_rules
from harness.explainability import format_comparison, format_findings, format_rule_log
from harness.financial_validator import validate_findings
from harness.fixture_catalog import FIXTURE_CATALOG, FixtureSpec
from harness.fixture_store import StoredFixture, build_fixture, load_fixture, save_fixture


@dataclass
class FixtureRunResult:
    fixture: StoredFixture
    passed: bool
    comparison: object
    financial: object
    findings: list
    logs: list
    errors: list[str]
    duration_ms: int
    id_maps: object


@dataclass
class HarnessRunResult:
    passed: bool
    fixture_results: list[FixtureRunResult] = field(default_factory=list)
    coverage: HarnessCoverageReport | None = None


def _rules_to_run(spec: FixtureSpec) -> list[str] | None:
    """Run rules in isolation unless the fixture is a full-suite negative or normal control."""
    if spec.fixture_type == "negative":
        return None
    if spec.fixture_id == "01_normal_company":
        return None
    if spec.rule_ids:
        return spec.rule_ids
    if spec.target_rules:
        return spec.target_rules
    return None


def run_fixture(fixture_id: str, *, verbose: bool = False) -> FixtureRunResult:
    fixture = load_fixture(fixture_id)
    start = time.perf_counter()

    ctx, id_maps = build_context_from_state(fixture.rows)
    rule_ids = _rules_to_run(fixture.spec)
    engine = run_all_rules(ctx, rule_ids=rule_ids)

    comparison = compare_findings(
        fixture.ground_truth.findings,
        engine.findings,
        id_maps,
        allow_extra=fixture.spec.allow_extra_findings,
    )
    financial = validate_findings(engine.findings)
    duration_ms = int((time.perf_counter() - start) * 1000)

    passed = comparison.passed and financial.passed and not engine.errors

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"FIXTURE: {fixture.spec.fixture_id}, {fixture.spec.name}")
        print(f"{'=' * 60}")
        print(fixture.spec.description)
        print()
        if engine.findings:
            print(format_findings(engine.findings, id_maps))
        else:
            print("No findings produced.")
        print()
        if not comparison.passed:
            print(format_comparison(comparison, id_maps))
        if not financial.passed:
            print(financial.summary())
        for log in engine.logs:
            print(format_rule_log(log))

    return FixtureRunResult(
        fixture=fixture,
        passed=passed,
        comparison=comparison,
        financial=financial,
        findings=engine.findings,
        logs=engine.logs,
        errors=engine.errors,
        duration_ms=duration_ms,
        id_maps=id_maps,
    )


def materialize_all_fixtures() -> list:
    from pathlib import Path

    written: list[Path] = []
    for spec in FIXTURE_CATALOG:
        rows, ground_truth = build_fixture(spec)
        path = save_fixture(spec, rows, ground_truth)
        written.append(path)
    return written


def run_all_fixtures(*, verbose: bool = False, fixture_ids: list[str] | None = None) -> HarnessRunResult:
    ids = fixture_ids or [spec.fixture_id for spec in FIXTURE_CATALOG]
    results: list[FixtureRunResult] = []

    for fixture_id in ids:
        result = run_fixture(fixture_id, verbose=verbose)
        results.append(result)

    coverage_fixtures = [
        FixtureResult(
            fixture_id=result.fixture.spec.fixture_id,
            passed=result.passed,
            comparison=result.comparison,
            financial=result.financial,
            duration_ms=result.duration_ms,
            errors=result.errors,
        )
        for result in results
    ]
    all_logs = [log for result in results for log in result.logs]
    coverage = build_coverage_report(coverage_fixtures, all_logs)

    return HarnessRunResult(
        passed=all(result.passed for result in results),
        fixture_results=results,
        coverage=coverage,
    )
