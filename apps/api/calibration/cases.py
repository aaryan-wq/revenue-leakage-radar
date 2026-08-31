"""Build audit-driven calibration cases."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from calibration.audit_runner import AuditResult, run_audit_on_rows
from calibration.profile_mapper import profile_to_questionnaire
from harness.company_generator import generate_company
from harness.fixture_store import FIXTURE_ROOT, load_rows_from_csv_dir
from harness.injections import ALL_RULE_IDS
from harness.types import CompanyProfile, GroundTruthDocument, GroundTruthFinding


@dataclass
class AuditCalibrationCase:
    case_id: str
    name: str
    answers: dict[str, Any]
    audit_target_usd: float
    injected_annual_usd: float
    audit: AuditResult
    source: str
    injected_rules: list[str]


MAX_AUDIT_INJECTED_DELTA_PCT = 25.0


def _audit_within_tolerance(audit: AuditResult, *, max_delta_pct: float = MAX_AUDIT_INJECTED_DELTA_PCT) -> bool:
    injected = audit.injected_annual_leakage
    if injected <= 0:
        return False
    delta = abs(audit.primary_recoverable_arr - injected) / injected * 100
    return delta <= max_delta_pct


def _case_from_ground_truth(
    *,
    case_id: str,
    name: str,
    rows: dict[str, list[dict]],
    ground_truth: GroundTruthDocument,
    source: str,
    max_audit_delta_pct: float = MAX_AUDIT_INJECTED_DELTA_PCT,
) -> AuditCalibrationCase | None:
    positives = [finding for finding in ground_truth.findings if not finding.is_negative]
    if not positives:
        return None
    audit = run_audit_on_rows(rows, ground_truth.findings)
    if audit.primary_recoverable_arr <= 0:
        return None
    if not _audit_within_tolerance(audit, max_delta_pct=max_audit_delta_pct):
        return None
    answers = profile_to_questionnaire(
        ground_truth.profile,
        injected_rules=ground_truth.injected_rules,
        ground_truth=ground_truth,
    )
    return AuditCalibrationCase(
        case_id=case_id,
        name=name,
        answers=answers,
        audit_target_usd=audit.primary_recoverable_arr,
        injected_annual_usd=audit.injected_annual_leakage,
        audit=audit,
        source=source,
        injected_rules=list(ground_truth.injected_rules),
    )


def build_cases_from_fixtures(
    *,
    fixture_ids: list[str] | None = None,
    require_single_injection: bool = False,
) -> list[AuditCalibrationCase]:
    cases: list[AuditCalibrationCase] = []
    if fixture_ids is None:
        fixture_dirs = sorted(
            path
            for path in FIXTURE_ROOT.iterdir()
            if path.is_dir() and (path / "ground_truth.json").exists()
        )
    else:
        fixture_dirs = [FIXTURE_ROOT / fixture_id for fixture_id in fixture_ids]

    for fixture_dir in fixture_dirs:
        if not fixture_dir.exists():
            continue
        case = load_fixture_case_from_dir(fixture_dir)
        if case is None:
            continue
        if require_single_injection and len(case.injected_rules) != 1:
            continue
        cases.append(case)
    return cases


def build_cases_from_seeds(
    seeds: list[int],
    *,
    customer_count: int = 100,
    product_count: int = 4,
    all_rules: bool = True,
    rule_id: str | None = None,
) -> list[AuditCalibrationCase]:
    cases: list[AuditCalibrationCase] = []
    for seed in seeds:
        if rule_id is not None:
            targets = [rule_id]
        elif all_rules:
            targets = ALL_RULE_IDS
        else:
            continue
        company = generate_company(
            seed=seed,
            customer_count=customer_count,
            product_count=product_count,
            rule_ids=targets,
            verification_mode=True,
        )
        case = _case_from_ground_truth(
            case_id=f"generated_{seed}" + (f"_{rule_id}" if rule_id else ""),
            name=f"Generated seed {seed}" + (f" ({rule_id})" if rule_id else ""),
            rows=company.rows(),
            ground_truth=company.ground_truth,
            source=f"generated:{seed}" + (f":{rule_id}" if rule_id else ""),
        )
        if case is not None:
            cases.append(case)
    return cases


def build_cases_from_single_rules(
    *,
    base_seed: int = 42,
    rule_ids: list[str] | None = None,
    customer_count: int = 100,
    product_count: int = 4,
    max_audit_delta_pct: float = MAX_AUDIT_INJECTED_DELTA_PCT,
) -> list[AuditCalibrationCase]:
    """One verification-mode company per rule with a deterministic seed."""
    cases: list[AuditCalibrationCase] = []
    targets = rule_ids or ALL_RULE_IDS
    for index, rule_id in enumerate(targets):
        seed = base_seed + index * 997
        company = generate_company(
            seed=seed,
            customer_count=customer_count,
            product_count=product_count,
            rule_ids=[rule_id],
            verification_mode=True,
        )
        case = _case_from_ground_truth(
            case_id=f"rule_{rule_id}",
            name=f"Single rule: {rule_id}",
            rows=company.rows(),
            ground_truth=company.ground_truth,
            source=f"generated:{seed}:{rule_id}",
            max_audit_delta_pct=max_audit_delta_pct,
        )
        if case is not None:
            cases.append(case)
    return cases


def load_fixture_case_from_dir(fixture_dir: Path) -> AuditCalibrationCase | None:
    gt_path = fixture_dir / "ground_truth.json"
    if not gt_path.exists():
        return None
    gt_data = json.loads(gt_path.read_text(encoding="utf-8"))
    findings = [GroundTruthFinding.from_dict(item) for item in gt_data.get("findings", [])]
    profile_data = gt_data["profile"]
    profile = CompanyProfile(
        company_id=profile_data["company_id"],
        name=profile_data["name"],
        industry=profile_data["industry"],
        arr_target=Decimal(str(profile_data["arr_target"])),
        customer_count=profile_data["customer_count"],
        product_count=profile_data["product_count"],
        billing_platform=profile_data["billing_platform"],
        crm_platform=profile_data["crm_platform"],
        currency=profile_data["currency"],
        locale=profile_data["locale"],
        pricing_strategy=profile_data["pricing_strategy"],
        seat_based=profile_data["seat_based"],
    )
    ground_truth = GroundTruthDocument(
        profile=profile,
        findings=findings,
        seed=gt_data.get("seed", 0),
        injected_rules=gt_data.get("injected_rules", []),
    )
    rows = load_rows_from_csv_dir(fixture_dir / "csvs")
    return _case_from_ground_truth(
        case_id=fixture_dir.name,
        name=fixture_dir.name,
        rows=rows,
        ground_truth=ground_truth,
        source=f"fixture:{fixture_dir.name}",
    )
