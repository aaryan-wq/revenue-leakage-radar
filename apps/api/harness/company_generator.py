"""Orchestrate synthetic company generation with ground truth."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from harness.baseline import build_baseline_state
from harness.clean_baseline import build_clean_baseline_state
from harness.company_state import CompanyState
from harness.context_loader import state_to_rows
from harness.csv_fuzzer import CsvFuzzConfig, export_csvs
from harness.injections import ALL_RULE_IDS, apply_injections
from harness.verification_repair import repair_baseline_after_injections
from harness.types import GroundTruthDocument, GroundTruthFinding


@dataclass
class GeneratedCompany:
    state: CompanyState
    ground_truth: GroundTruthDocument
    seed: int

    def rows(self) -> dict:
        return state_to_rows(self.state)

    def write_ground_truth(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.ground_truth.to_dict(), indent=2), encoding="utf-8")

    def export_csvs(self, output_dir: Path, rng: random.Random, fuzz: CsvFuzzConfig | None = None) -> dict[str, Path]:
        return export_csvs(self.rows(), output_dir, rng, fuzz)


def generate_company(
    seed: int | None = None,
    customer_count: int = 50,
    product_count: int = 4,
    rule_ids: list[str] | None = None,
    include_crm: bool = True,
    *,
    verification_mode: bool = False,
) -> GeneratedCompany:
    seed = seed if seed is not None else random.randint(0, 2**31 - 1)
    rng = random.Random(seed)
    if verification_mode:
        state = build_clean_baseline_state(
            rng,
            customer_count=customer_count,
            product_count=product_count,
            include_crm=include_crm,
        )
    else:
        state = build_baseline_state(
            rng,
            customer_count=customer_count,
            product_count=product_count,
            include_crm=include_crm,
        )
    targets = rule_ids or ALL_RULE_IDS
    apply_injections(state, rng, targets)

    if verification_mode:
        injected_subscriptions = {
            finding.subscription_id for finding in state.ground_truth if finding.subscription_id
        }
        repair_baseline_after_injections(
            state,
            injected_subscriptions,
            ground_truth=state.ground_truth,
        )

    doc = GroundTruthDocument(
        profile=state.profile,
        findings=list(state.ground_truth),
        seed=seed,
        injected_rules=targets,
    )
    return GeneratedCompany(state=state, ground_truth=doc, seed=seed)


def strip_internal_fields(state: CompanyState) -> None:
    for sub in state.subscriptions:
        sub.pop("_plan", None)
        sub.pop("_end_date", None)
