#!/usr/bin/env python3
"""Verify full_suite_all_rules dataset against the verification engine."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
API_ROOT = REPO_ROOT / "apps" / "api"
DATA_DIR = REPO_ROOT / "testdata" / "full_suite_all_rules"

sys.path.insert(0, str(API_ROOT))

from harness.comparator import compare_findings  # noqa: E402
from harness.context_loader import load_context_from_csv_dir  # noqa: E402
from harness.engine_runner import run_all_rules  # noqa: E402
from harness.injections import ALL_RULE_IDS  # noqa: E402
from harness.types import GroundTruthFinding  # noqa: E402


def main() -> int:
    if not DATA_DIR.exists():
        print(f"Dataset not found at {DATA_DIR}")
        print("Run: python scripts/generate_full_suite_dataset.py")
        return 1

    gt_path = DATA_DIR / "ground_truth.json"
    ground_truth = json.loads(gt_path.read_text(encoding="utf-8"))
    findings = [GroundTruthFinding.from_dict(item) for item in ground_truth.get("findings", [])]

    ctx, id_maps = load_context_from_csv_dir(DATA_DIR)
    engine = run_all_rules(ctx)
    comparison = compare_findings(findings, engine.findings, id_maps, allow_extra=True)

    injected_rules = {f.rule_id for f in findings if not f.is_negative}
    missing_rules = set(ALL_RULE_IDS) - injected_rules - {"orphaned_records"}

    print("=" * 60)
    print("FULL SUITE DATASET VERIFICATION")
    print("=" * 60)
    print(f"Ground truth findings:  {len(findings)}")
    print(f"Engine findings:        {len(engine.findings)}")
    print(f"Rules in ground truth:  {len(injected_rules)}/{len(ALL_RULE_IDS)}")
    print(f"Rules fired by engine:  {len({f.rule_id for f in engine.findings})}/{len(ALL_RULE_IDS)}")
    print(f"Ground truth match:     {comparison.matched}/{comparison.expected_count}")
    print()

    if missing_rules:
        print("Missing rules in ground truth:")
        for rule_id in sorted(missing_rules):
            print(f"  - {rule_id}")
        print()

    if not comparison.passed:
        print("Mismatches:")
        for mismatch in comparison.mismatches[:15]:
            print(f"  [{mismatch.kind}] {mismatch.rule_id}: {mismatch.message}")
        if len(comparison.mismatches) > 15:
            print(f"  ... and {len(comparison.mismatches) - 15} more")
        print()

    passed = (
        not missing_rules
        and comparison.passed
        and not engine.errors
        and len(injected_rules) == len(ALL_RULE_IDS) - 1
    )
    print("RESULT:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
