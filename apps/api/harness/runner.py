"""Main harness iteration loop."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory

from harness.company_generator import GeneratedCompany, generate_company
from harness.comparator import ComparisonResult, compare_findings
from harness.context_loader import build_context_from_state
from harness.csv_fuzzer import CsvFuzzConfig
from harness.engine_runner import run_all_rules
from harness.regression import save_regression_case


@dataclass
class HarnessConfig:
    iterations: int = 10
    customer_count: int = 50
    product_count: int = 4
    rule_ids: list[str] | None = None
    seed: int | None = None
    fuzz_csv: bool = True
    save_failures: bool = True
    allow_extra_findings: bool = True
    company_sizes: list[int] | None = None


@dataclass
class HarnessResult:
    passed: bool
    iterations_run: int
    iterations_passed: int
    total_mismatches: int
    duration_seconds: float
    results: list[ComparisonResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def run_harness_iteration(
    seed: int | None = None,
    customer_count: int = 50,
    product_count: int = 4,
    rule_ids: list[str] | None = None,
    fuzz_csv: bool = False,
    allow_extra_findings: bool = True,
) -> tuple[ComparisonResult, GeneratedCompany, list[str]]:
    company = generate_company(
        seed=seed,
        customer_count=customer_count,
        product_count=product_count,
        rule_ids=rule_ids,
    )
    ctx, id_maps = build_context_from_state(company.rows())
    engine_result = run_all_rules(ctx)

    comparison = compare_findings(
        company.ground_truth.findings,
        engine_result.findings,
        id_maps,
        allow_extra=allow_extra_findings,
    )
    return comparison, company, engine_result.errors


def run_harness(config: HarnessConfig | None = None) -> HarnessResult:
    config = config or HarnessConfig()
    start = time.perf_counter()
    results: list[ComparisonResult] = []
    passed_count = 0
    total_mismatches = 0
    all_errors: list[str] = []

    sizes = config.company_sizes or [config.customer_count]
    base_seed = config.seed if config.seed is not None else random.randint(0, 2**31 - 1)

    for iteration in range(config.iterations):
        seed = base_seed + iteration
        customer_count = sizes[iteration % len(sizes)]
        comparison, company, errors = run_harness_iteration(
            seed=seed,
            customer_count=customer_count,
            product_count=config.product_count,
            rule_ids=config.rule_ids,
            fuzz_csv=config.fuzz_csv,
            allow_extra_findings=config.allow_extra_findings,
        )
        results.append(comparison)
        all_errors.extend(errors)

        if comparison.passed and not errors:
            passed_count += 1
        else:
            total_mismatches += len(comparison.mismatches)
            if config.save_failures and comparison.mismatches:
                first = comparison.mismatches[0]
                case_id = f"{first.rule_id}_{seed}"
                with TemporaryDirectory() as tmp:
                    tmp_path = Path(tmp)
                    if config.fuzz_csv:
                        rng = random.Random(seed)
                        fuzz = CsvFuzzConfig(platform=company.state.profile.billing_platform)
                        company.export_csvs(tmp_path, rng, fuzz)
                    save_regression_case(
                        case_id=case_id,
                        rule_id=first.rule_id,
                        seed=seed,
                        ground_truth=company.ground_truth.to_dict(),
                        mismatch_summary=first.message,
                        csv_dir=tmp_path if config.fuzz_csv else None,
                    )

    duration = time.perf_counter() - start
    return HarnessResult(
        passed=passed_count == config.iterations and not all_errors,
        iterations_run=config.iterations,
        iterations_passed=passed_count,
        total_mismatches=total_mismatches,
        duration_seconds=duration,
        results=results,
        errors=all_errors,
    )
