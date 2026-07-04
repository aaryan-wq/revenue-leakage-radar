"""Regression suite persistence for discovered harness failures."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REGRESSION_ROOT = Path(__file__).resolve().parent.parent / "tests" / "harness_regressions"


@dataclass
class RegressionCase:
    case_id: str
    rule_id: str
    seed: int
    path: Path


def save_regression_case(
    case_id: str,
    rule_id: str,
    seed: int,
    ground_truth: dict,
    mismatch_summary: str,
    csv_dir: Path | None = None,
) -> Path:
    case_dir = REGRESSION_ROOT / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "case_id": case_id,
        "rule_id": rule_id,
        "seed": seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mismatch": mismatch_summary,
    }
    (case_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (case_dir / "ground_truth.json").write_text(json.dumps(ground_truth, indent=2), encoding="utf-8")

    if csv_dir and csv_dir.exists():
        dest = case_dir / "csvs"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(csv_dir, dest)

    return case_dir


def list_regression_cases() -> list[RegressionCase]:
    if not REGRESSION_ROOT.exists():
        return []
    cases: list[RegressionCase] = []
    for path in sorted(REGRESSION_ROOT.iterdir()):
        if not path.is_dir():
            continue
        meta_path = path / "meta.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        cases.append(
            RegressionCase(
                case_id=meta["case_id"],
                rule_id=meta["rule_id"],
                seed=meta["seed"],
                path=path,
            )
        )
    return cases
