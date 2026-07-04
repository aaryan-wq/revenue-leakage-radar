#!/usr/bin/env python3
"""Run the verification engine harness against all deterministic fixtures."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harness.fixture_catalog import FIXTURE_CATALOG, all_fixture_ids
from harness.fixture_runner import run_all_fixtures, run_fixture


def main() -> int:
    parser = argparse.ArgumentParser(description="Verification Engine Test Harness")
    parser.add_argument(
        "--fixture",
        action="append",
        dest="fixtures",
        help="Run a specific fixture (repeatable). Default: all fixtures.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print explainability output for each finding.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available fixtures and exit.",
    )
    args = parser.parse_args()

    if args.list:
        for spec in FIXTURE_CATALOG:
            print(f"{spec.fixture_id:40s} {spec.name}")
        return 0

    fixture_ids = args.fixtures or all_fixture_ids()

    if len(fixture_ids) == 1 and args.verbose:
        result = run_fixture(fixture_ids[0], verbose=True)
        passed = result.passed
    else:
        harness = run_all_fixtures(fixture_ids=fixture_ids, verbose=args.verbose)
        passed = harness.passed
        if harness.coverage:
            print(harness.coverage.to_text())

    if passed:
        print("\nPASS: All fixtures passed, engine matches ground truth.")
        return 0

    print("\nFAIL: Harness failed, see mismatches above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
