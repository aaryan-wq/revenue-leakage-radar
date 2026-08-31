#!/usr/bin/env python3
"""Audit-driven estimator calibration loop.

Generate synthetic billing companies (or reuse verification fixtures), run the
deterministic verification engine on harness CSV rows, map the company profile
to questionnaire answers, compare estimator output to audit recoverable ARR,
and optionally grid-search prior knobs to close the gap.

Examples:

  python scripts/calibration_loop.py compare --single-only
  python scripts/calibration_loop.py compare --seeds 991337
  python scripts/calibration_loop.py loop --single-only --apply --max-passes 5 --target-error 35
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
API_ROOT = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from calibration.cases import (  # noqa: E402
    FIXTURE_ROOT,
    build_cases_from_seeds,
    build_cases_from_single_rules,
    load_fixture_case_from_dir,
)
from harness.injections import ALL_RULE_IDS  # noqa: E402
from calibration.compare import compare_cases, format_comparison_table, max_abs_error, mean_abs_error  # noqa: E402
from calibration.tune import (  # noqa: E402
    TuneConfig,
    apply_config_to_priors,
    compute_rule_prior_adjustments,
    grid_search,
    iterative_search,
    safe_apply_rule_overlay,
    _load_overlay_multipliers,
)


def _parse_seeds(raw: str | None) -> list[int]:
    if not raw:
        return []
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def _build_cases(args: argparse.Namespace):
    max_delta = float(getattr(args, "max_audit_delta", 25.0))
    cases = []
    if args.fixtures:
        for fixture_dir in sorted(
            path
            for path in FIXTURE_ROOT.iterdir()
            if path.is_dir() and (path / "ground_truth.json").exists()
        ):
            case = load_fixture_case_from_dir(fixture_dir)
            if case is None:
                continue
            if args.single_only and len(case.injected_rules) != 1:
                continue
            delta = abs(case.audit.primary_recoverable_arr - case.injected_annual_usd)
            if case.injected_annual_usd > 0:
                pct = delta / case.injected_annual_usd * 100
                if pct > max_delta:
                    continue
            cases.append(case)
    seeds = _parse_seeds(args.seeds)
    if seeds:
        for index, seed in enumerate(seeds):
            if args.single_only:
                rule_arg = (getattr(args, "rule", "") or "").strip()
                rule_id = rule_arg or ALL_RULE_IDS[index % len(ALL_RULE_IDS)]
                cases.extend(
                    build_cases_from_seeds(
                        [seed],
                        customer_count=args.customers,
                        all_rules=False,
                        rule_id=rule_id,
                    )
                )
            else:
                cases.extend(
                    build_cases_from_seeds(
                        [seed],
                        customer_count=args.customers,
                        all_rules=True,
                    )
                )
    elif args.single_only and not args.fixtures:
        cases.extend(
            build_cases_from_single_rules(
                base_seed=args.seed,
                customer_count=args.customers,
                max_audit_delta_pct=max_delta,
            )
        )
    if args.limit and len(cases) > args.limit:
        cases = cases[: args.limit]
    return cases


def cmd_compare(args: argparse.Namespace) -> int:
    cases = _build_cases(args)
    if not cases:
        print("No calibration cases built. Use --fixtures and/or --seeds.")
        return 1
    print(f"Built {len(cases)} audit calibration case(s).\n")
    rows, _ = compare_cases(cases, random_seed=args.seed)
    print(format_comparison_table(rows))
    print(
        f"\nAudit vs injected mean delta: "
        f"{sum(r.audit_vs_injected_pct for r in rows) / len(rows):+.1f}%"
    )
    return 0


def cmd_tune(args: argparse.Namespace) -> int:
    cases = _build_cases(args)
    if not cases:
        print("No calibration cases built. Use --fixtures and/or --seeds.")
        return 1
    print(f"Tuning against {len(cases)} audit calibration case(s)...\n")
    if args.iterations > 1:
        result = iterative_search(cases, iterations=args.iterations, random_seed=args.seed)
    else:
        result = grid_search(cases, random_seed=args.seed)

    print("Best configuration:")
    print(f"  complexity_scale.base = {result.config.complexity_base}")
    print(f"  affected_rate.beta    = {result.config.affected_beta}")
    print(f"  rule_prior_multiplier = {result.config.rule_prior_multiplier}")
    print(f"  mean abs error        = {result.mean_abs_error_pct:.1f}%")
    print(f"  max abs error         = {result.max_abs_error_pct:.1f}%")
    print()
    print(format_comparison_table(result.rows))

    if args.apply:
        adjustments = compute_rule_prior_adjustments(cases, result.rows)
        updated, ok = safe_apply_rule_overlay(adjustments)
        if ok and updated:
            print(f"\nApplied {updated} rule overlay multiplier(s) to audit-calibration.yaml.")
        elif not ok:
            print("\nSkipped overlay apply: hand-calibrated fixtures would fail.")
        apply_config_to_priors(result.config)
        print("Updated MC knobs in priors.yaml (if changed).")
    return 0


def cmd_loop(args: argparse.Namespace) -> int:
    baseline_err = 999.0
    for pass_num in range(1, args.max_passes + 1):
        cases = _build_cases(args)
        if not cases:
            print("No calibration cases built.")
            return 1
        print(f"\n=== Pass {pass_num}/{args.max_passes} ({len(cases)} cases) ===\n")
        rows, _ = compare_cases(cases, random_seed=args.seed)
        baseline_err = mean_abs_error(rows)
        print(format_comparison_table(rows))
        print(f"\nRule-level mean abs error: {baseline_err:.1f}%")
        if baseline_err <= args.target_error:
            print(f"Target error ({args.target_error}%) reached.")
            return 0

        adjustments = compute_rule_prior_adjustments(cases, rows)
        if adjustments:
            print("\nProposed audit-calibration overlay multipliers:")
            for rule_id, mult in sorted(adjustments.items()):
                print(f"  {rule_id}: x{mult:.3f}")
            if args.apply:
                updated, ok = safe_apply_rule_overlay(adjustments)
                if ok and updated:
                    print(f"\nSaved overlay recommendations for {updated} rule(s) (tooling only).")
                    rows, _ = compare_cases(
                        cases,
                        random_seed=args.seed,
                        overlay_multipliers=_load_overlay_multipliers(),
                    )
                    baseline_err = mean_abs_error(rows)
                    print(format_comparison_table(rows))
                    print(f"\nAfter overlay: {baseline_err:.1f}%")
                    if baseline_err <= args.target_error:
                        print(f"Target error ({args.target_error}%) reached.")
                        return 0
                elif not ok:
                    print("\nOverlay rejected: hand-calibrated fixtures would fail.")

        if baseline_err <= args.target_error:
            return 0

        if pass_num == args.max_passes:
            break

    print(f"\nStopped after {args.max_passes} passes (rule-level mean abs error {baseline_err:.1f}%).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit-driven estimator calibration loop")
    sub = parser.add_subparsers(dest="command", required=True)

    compare_parser = sub.add_parser("compare", help="Compare estimator vs audit targets")
    tune_parser = sub.add_parser("tune", help="Grid-search prior knobs against audit targets")

    for sub_parser in (compare_parser, tune_parser):
        sub_parser.add_argument("--fixtures", action="store_true", help="Include verification fixtures")
        sub_parser.add_argument(
            "--single-only",
            action="store_true",
            help="Use single-rule injection fixtures / one injection per generated company",
        )
        sub_parser.add_argument("--seeds", type=str, default="", help="Comma-separated generation seeds")
        sub_parser.add_argument("--customers", type=int, default=100, help="Customers for generated companies")
        sub_parser.add_argument("--limit", type=int, default=0, help="Limit number of cases (0 = all)")
        sub_parser.add_argument("--seed", type=int, default=42, help="Estimator Monte Carlo seed")
        sub_parser.add_argument(
            "--max-audit-delta",
            type=float,
            default=25.0,
            help="Skip cases where audit primary ARR deviates more than this pct from injected leakage",
        )
        sub_parser.add_argument(
            "--rule",
            type=str,
            default="",
            help="Single rule id when using --single-only with --seeds",
        )

    loop_parser = sub.add_parser("loop", help="Iteratively tune until error threshold or max passes")
    loop_parser.add_argument("--fixtures", action="store_true")
    loop_parser.add_argument("--single-only", action="store_true")
    loop_parser.add_argument("--seeds", type=str, default="")
    loop_parser.add_argument("--customers", type=int, default=100)
    loop_parser.add_argument("--limit", type=int, default=0)
    loop_parser.add_argument("--seed", type=int, default=42)
    loop_parser.add_argument("--max-audit-delta", type=float, default=25.0)
    loop_parser.add_argument("--rule", type=str, default="")
    loop_parser.add_argument(
        "--target-error",
        type=float,
        default=30.0,
        help="Stop when mean abs error below this pct",
    )
    loop_parser.add_argument("--max-passes", type=int, default=5, help="Maximum tune passes")
    loop_parser.add_argument("--apply", action="store_true", help="Save fixture-safe overlay recommendations")

    tune_parser.add_argument("--iterations", type=int, default=2, help="Grid search passes")
    tune_parser.add_argument(
        "--apply",
        action="store_true",
        help="Print YAML apply instructions for the best configuration",
    )

    args = parser.parse_args()
    if args.command == "compare":
        return cmd_compare(args)
    if args.command == "loop":
        return cmd_loop(args)
    return cmd_tune(args)


if __name__ == "__main__":
    raise SystemExit(main())
