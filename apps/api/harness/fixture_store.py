"""Persist and load verification fixtures from disk."""

from __future__ import annotations

import csv
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from harness.company_generator import GeneratedCompany, generate_company
from harness.fixture_catalog import FixtureSpec, get_fixture_spec
from harness.minimal_fixtures import MINIMAL_BUILDERS, MinimalFixture
from harness.types import GroundTruthDocument, GroundTruthFinding

FIXTURE_ROOT = Path(__file__).resolve().parent.parent / "tests" / "verification_fixtures"

ENTITY_FILES = (
    "customers",
    "subscriptions",
    "invoices",
    "invoice_line_items",
    "coupons",
    "price_catalog",
    "crm_accounts",
    "crm_contracts",
)


@dataclass
class StoredFixture:
    spec: FixtureSpec
    rows: dict[str, list[dict]]
    ground_truth: GroundTruthDocument
    path: Path


def build_fixture(spec: FixtureSpec) -> tuple[dict[str, list[dict]], GroundTruthDocument]:
    if spec.fixture_id in MINIMAL_BUILDERS:
        minimal = MINIMAL_BUILDERS[spec.fixture_id]()
        return minimal.rows, minimal.ground_truth

    company: GeneratedCompany = generate_company(
        seed=spec.seed,
        customer_count=spec.customer_count,
        rule_ids=spec.rule_ids or [],
    )
    return company.rows(), company.ground_truth


def export_canonical_csvs(rows: dict[str, list[dict]], output_dir: Path) -> None:
    """Write canonical CSV files without header fuzzing or date reformatting."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for entity in ENTITY_FILES:
        entity_rows = rows.get(entity, [])
        if not entity_rows:
            continue
        public = [{k: str(v) for k, v in row.items() if not str(k).startswith("_")} for row in entity_rows]
        if not public:
            continue
        path = output_dir / f"{entity}.csv"
        fieldnames = list(public[0].keys())
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(public)


def save_fixture(spec: FixtureSpec, rows: dict[str, list[dict]], ground_truth: GroundTruthDocument) -> Path:
    fixture_dir = FIXTURE_ROOT / spec.fixture_id
    csv_dir = fixture_dir / "csvs"
    if fixture_dir.exists():
        shutil.rmtree(fixture_dir)
    fixture_dir.mkdir(parents=True)
    csv_dir.mkdir()

    meta = {
        "fixture_id": spec.fixture_id,
        "name": spec.name,
        "description": spec.description,
        "fixture_type": spec.fixture_type,
        "target_rules": spec.target_rules,
        "seed": spec.seed,
        "rule_ids": spec.rule_ids,
        "customer_count": spec.customer_count,
        "allow_extra_findings": spec.allow_extra_findings,
    }
    (fixture_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (fixture_dir / "ground_truth.json").write_text(
        json.dumps(ground_truth.to_dict(), indent=2),
        encoding="utf-8",
    )
    export_canonical_csvs(rows, csv_dir)
    return fixture_dir


def load_rows_from_csv_dir(csv_dir: Path) -> dict[str, list[dict]]:
    rows: dict[str, list[dict]] = {}
    for entity in ENTITY_FILES:
        path = csv_dir / f"{entity}.csv"
        if not path.exists():
            rows[entity] = []
            continue
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows[entity] = list(csv.DictReader(handle))
    return rows


def load_fixture(fixture_id: str) -> StoredFixture:
    spec = get_fixture_spec(fixture_id)
    if spec is None:
        raise ValueError(f"Unknown fixture: {fixture_id}")

    fixture_dir = FIXTURE_ROOT / fixture_id
    if not fixture_dir.exists():
        rows, ground_truth = build_fixture(spec)
        save_fixture(spec, rows, ground_truth)
        fixture_dir = FIXTURE_ROOT / fixture_id

    meta = json.loads((fixture_dir / "meta.json").read_text(encoding="utf-8"))
    spec = FixtureSpec(
        fixture_id=meta["fixture_id"],
        name=meta["name"],
        description=meta["description"],
        fixture_type=meta["fixture_type"],
        target_rules=meta.get("target_rules", []),
        seed=meta.get("seed"),
        rule_ids=meta.get("rule_ids"),
        customer_count=meta.get("customer_count", 50),
        allow_extra_findings=bool(meta.get("allow_extra_findings", False)),
    )
    gt_data = json.loads((fixture_dir / "ground_truth.json").read_text(encoding="utf-8"))
    findings = [GroundTruthFinding.from_dict(item) for item in gt_data.get("findings", [])]
    from decimal import Decimal
    from harness.types import CompanyProfile

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
    return StoredFixture(spec=spec, rows=rows, ground_truth=ground_truth, path=fixture_dir)


def list_stored_fixtures() -> list[str]:
    if not FIXTURE_ROOT.exists():
        return []
    return sorted(
        path.name
        for path in FIXTURE_ROOT.iterdir()
        if path.is_dir() and (path / "meta.json").exists()
    )
