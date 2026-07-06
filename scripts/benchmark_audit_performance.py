#!/usr/bin/env python3
"""Benchmark verification engine performance at increasing customer scales."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api"))

from harness.company_generator import generate_company
from harness.context_loader import build_context_from_state
from harness.engine_runner import run_all_rules


def benchmark(customer_count: int, seed: int) -> dict[str, float]:
    start = time.perf_counter()
    company = generate_company(seed=seed, customer_count=customer_count, verification_mode=True)
    gen_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    ctx, _ = build_context_from_state(company.rows())
    context_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    result = run_all_rules(ctx)
    engine_ms = (time.perf_counter() - start) * 1000

    return {
        "customers": float(customer_count),
        "findings": float(len(result.findings)),
        "generate_ms": gen_ms,
        "context_ms": context_ms,
        "engine_ms": engine_ms,
        "total_ms": gen_ms + context_ms + engine_ms,
        "errors": float(len(result.errors)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark audit verification performance")
    parser.add_argument(
        "--sizes",
        nargs="*",
        type=int,
        default=[10, 100, 500, 1000],
        help="Customer counts to benchmark",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--max-engine-ms",
        type=int,
        default=0,
        help="Fail if engine time at largest size exceeds threshold (0 = no gate)",
    )
    args = parser.parse_args()

    print(f"{'Customers':>10} {'Findings':>10} {'Generate':>12} {'Context':>12} {'Engine':>12} {'Total':>12}")
    print("-" * 72)
    largest_engine = 0.0
    for size in args.sizes:
        row = benchmark(size, args.seed + size)
        largest_engine = max(largest_engine, row["engine_ms"])
        print(
            f"{int(row['customers']):>10} "
            f"{int(row['findings']):>10} "
            f"{row['generate_ms']:>10.0f}ms "
            f"{row['context_ms']:>10.0f}ms "
            f"{row['engine_ms']:>10.0f}ms "
            f"{row['total_ms']:>10.0f}ms"
        )
        if row["errors"] > 0:
            print(f"  WARNING: {int(row['errors'])} engine errors")

    if args.max_engine_ms > 0 and largest_engine > args.max_engine_ms:
        print(
            f"\nFAIL: largest engine time {largest_engine:.0f}ms exceeds "
            f"threshold {args.max_engine_ms}ms"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
