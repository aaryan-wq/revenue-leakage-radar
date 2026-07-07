#!/usr/bin/env python3
"""Verify a generated verification dataset (all 26 rules)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
API_ROOT = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from harness.comparator import compare_findings  # noqa: E402
from harness.context_loader import load_context_from_csv_dir  # noqa: E402
from harness.engine_runner import run_all_rules  # noqa: E402
from harness.injections import ALL_RULE_IDS  # noqa: E402
from harness.types import GroundTruthFinding  # noqa: E402
from verification_dataset import UPLOAD_RULE_IDS  # noqa: E402


def resolve_run_dir(seed: int | None, run_dir: Path | None) -> Path:
    if run_dir is not None:
        return run_dir
    if seed is None:
        latest_seed = REPO_ROOT / "testdata" / "latest_seed.txt"
        if latest_seed.exists():
            seed = int(latest_seed.read_text(encoding="utf-8").strip())
        else:
            raise SystemExit("Provide --seed or --dir, or run generate_verification_dataset.py first")
    return REPO_ROOT / "testdata" / "runs" / f"run_{seed}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a generated verification dataset.")
    parser.add_argument("--seed", type=int, default=None, help="Seed used when generating the run")
    parser.add_argument("--dir", type=Path, default=None, help="Path to run directory")
    args = parser.parse_args()

    run_dir = resolve_run_dir(args.seed, args.dir)
    upload_dir = run_dir / "upload"
    harness_dir = run_dir / "harness"
    if not harness_dir.exists():
        print(f"Harness directory not found: {harness_dir}")
        print("Re-run: python scripts/generate_verification_dataset.py --seed <seed>")
        return 1
    if not upload_dir.exists():
        print(f"Upload directory not found: {upload_dir}")
        return 1

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    seed = manifest["seed"]
    findings = [
        GroundTruthFinding.from_dict(item)
        for item in json.loads((run_dir / "ground_truth.json").read_text(encoding="utf-8"))["findings"]
    ]
    positive_gt = [f for f in findings if not f.is_negative]

    ctx_upload, maps_upload = load_context_from_csv_dir(upload_dir)
    upload_engine = run_all_rules(ctx_upload)
    upload_gt = [f for f in positive_gt if f.rule_id in UPLOAD_RULE_IDS]
    upload_cmp = compare_findings(upload_gt, upload_engine.findings, maps_upload, allow_extra=True)

    ctx_harness, maps_harness = load_context_from_csv_dir(harness_dir)
    harness_engine = run_all_rules(ctx_harness)
    all_rules_cmp = compare_findings(positive_gt, harness_engine.findings, maps_harness, allow_extra=True)

    print("=" * 60)
    print(f"VERIFY RUN seed={seed}")
    print("=" * 60)
    print(f"Upload CSVs ({len(ALL_RULE_IDS)}):   {upload_cmp.matched}/{upload_cmp.expected_count} ground truth matched")
    print(f"Harness CSVs ({len(ALL_RULE_IDS)}):  {all_rules_cmp.matched}/{all_rules_cmp.expected_count} ground truth matched")
    print(f"Injected ARR:       ${manifest['injected_leakage_annual']}")
    print(f"Upload primary ARR: ${manifest.get('upload_primary_arr', '-')}")
    print()

    passed = (
        upload_cmp.passed
        and all_rules_cmp.passed
        and all_rules_cmp.matched == len(ALL_RULE_IDS)
        and len(positive_gt) == len(ALL_RULE_IDS)
    )
    print("RESULT:", "PASS" if passed else "FAIL")
    if not upload_cmp.passed:
        for mismatch in upload_cmp.mismatches[:5]:
            print(f"  upload: {mismatch.rule_id}, {mismatch.message}")
    if not all_rules_cmp.passed:
        for mismatch in all_rules_cmp.mismatches[:5]:
            print(f"  harness: {mismatch.rule_id}, {mismatch.message}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
