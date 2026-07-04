#!/usr/bin/env python3
"""Regenerate the canonical full_suite_all_rules dataset (seed 4242)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from verification_dataset import DatasetConfig, generate_dataset, sum_leakage  # noqa: E402

SEED = 4242
OUTPUT = REPO_ROOT / "testdata" / "full_suite_all_rules"


def main() -> int:
    config = DatasetConfig(seed=SEED, customer_count=100, output_dir=OUTPUT)
    result = generate_dataset(config)
    monthly, annual = sum_leakage(result.company.ground_truth.findings)

    upload_dir = result.output_dir / "upload"
    for csv in upload_dir.glob("*.csv"):
        dest = result.output_dir / csv.name
        if dest.exists():
            dest.unlink()
        csv.rename(dest)
    upload_dir.rmdir()

    print(f"Regenerated {OUTPUT} (seed {SEED})")
    print(f"  Injected ARR: ${annual:,.2f}")
    return 0 if result.upload_comparison.passed and result.full_comparison.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
