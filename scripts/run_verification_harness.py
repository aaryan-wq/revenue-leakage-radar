#!/usr/bin/env python3
"""Run the verification fuzz harness in a continuous self-test loop."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api"))

from harness.injections import ALL_RULE_IDS
from harness.runner import HarnessConfig, run_harness


def main() -> None:
    parser = argparse.ArgumentParser(description="Revenue Leakage Radar verification harness")
    parser.add_argument("--iterations", type=int, default=20, help="Fuzz iterations per run")
    parser.add_argument("--seed", type=int, default=None, help="Base RNG seed")
    parser.add_argument("--customers", type=int, default=50, help="Customers per synthetic company")
    parser.add_argument("--rules", nargs="*", default=None, help="Rule IDs to inject (default: all)")
    parser.add_argument(
        "--sizes",
        nargs="*",
        type=int,
        default=None,
        help="Rotate company sizes (e.g. 10 100 1000)",
    )
    parser.add_argument("--until-stable", action="store_true", help="Repeat batches until all pass")
    parser.add_argument("--max-rounds", type=int, default=5, help="Max rounds when --until-stable")
    args = parser.parse_args()

    round_num = 0
    while True:
        round_num += 1
        config = HarnessConfig(
            iterations=args.iterations,
            customer_count=args.customers,
            rule_ids=args.rules or ALL_RULE_IDS,
            seed=args.seed,
            company_sizes=args.sizes,
            fuzz_csv=True,
            save_failures=True,
            allow_extra_findings=True,
        )
        result = run_harness(config)

        print(f"Round {round_num}: {result.iterations_passed}/{result.iterations_run} passed")
        print(f"  Duration: {result.duration_seconds:.2f}s")
        print(f"  Mismatches: {result.total_mismatches}")
        if result.errors:
            print(f"  Engine errors: {len(result.errors)}")
            for err in result.errors[:5]:
                print(f"    - {err}")

        for index, comparison in enumerate(result.results):
            if not comparison.passed:
                print(comparison.summary())

        if result.passed:
            print("Harness stable, all iterations passed.")
            sys.exit(0)

        if not args.until_stable or round_num >= args.max_rounds:
            print("Harness finished with failures.")
            sys.exit(1)

        if args.seed is not None:
            args.seed += args.iterations


if __name__ == "__main__":
    main()
