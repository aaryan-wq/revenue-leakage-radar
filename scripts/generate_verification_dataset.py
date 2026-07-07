#!/usr/bin/env python3
"""Generate a fresh verification dataset (new seed, new leakage, all 26 rules)."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from verification_dataset import (  # noqa: E402
    DatasetConfig,
    generate_dataset,
    generate_viable_dataset,
    pick_seed,
    sum_leakage,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate fresh CSV test data with injected leakage for all 26 verification rules.",
    )
    parser.add_argument(
        "--seed",
        nargs="?",
        const=-1,
        default=None,
        type=int,
        metavar="N",
        help=(
            "Reproducible seed (e.g. --seed 991337). "
            "Omit N or omit this flag entirely to auto-pick a random viable seed (retries up to --max-attempts)."
        ),
    )
    parser.add_argument(
        "--customers",
        type=int,
        default=100,
        help="Number of customers in synthetic company (default: 100)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: testdata/runs/run_<seed>)",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=50,
        help="When auto-picking a seed, retry up to this many times until ARR tolerance passes (default: 50)",
    )
    args = parser.parse_args()

    # None = flag omitted; -1 = `--seed` with no value (both auto-pick)
    explicit_seed = args.seed is not None and args.seed >= 0
    seed = args.seed if explicit_seed else pick_seed(None)
    config = DatasetConfig(
        seed=seed,
        customer_count=args.customers,
        output_dir=args.output,
    )
    if explicit_seed:
        result = generate_dataset(config)
    else:
        result = generate_viable_dataset(config, max_attempts=args.max_attempts)
        seed = result.config.seed
    monthly, annual = sum_leakage(result.company.ground_truth.findings)

    upload_dir = result.output_dir / "upload"
    print(f"Generated verification run: {result.output_dir}")
    print(f"  Seed:           {seed}")
    print(f"  Upload CSVs:    {upload_dir}")
    print(
        f"  Rules injected: {result.all_rules_comparison.expected_count}/"
        f"{result.all_rules_comparison.expected_count}"
    )
    print(f"  Upload GT:      {result.upload_comparison.matched}/{result.upload_comparison.expected_count} matched")
    print(f"  All rules GT:   {result.all_rules_comparison.matched}/{result.all_rules_comparison.expected_count} matched")
    print(f"  Injected ARR:   ${annual:,.2f}  (${monthly:,.2f}/mo), ground truth only")
    manifest = json.loads((result.output_dir / "manifest.json").read_text(encoding="utf-8"))
    print(f"  Scan primary:   ${Decimal(manifest['upload_primary_arr']):,.2f}, expected app headline ARR")
    print()
    print("Upload the 8 CSVs from the upload/ folder, then verify:")
    print(f"  python scripts/verify_verification_dataset.py --seed {seed}")

    if not result.upload_comparison.passed or not result.all_rules_comparison.passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
