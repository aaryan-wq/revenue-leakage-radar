"""Load AcmeCRM CSVs through harness context loader (production-shaped canonical rows)."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "api"))
sys.path.insert(0, str(ROOT / "scripts"))

from harness.context_loader import _load_rows_from_dir, build_context_from_state
from verification.attribution import attribute_findings, sum_primary_recoverable_arr
from verification.registry import get_all_rules

DATA = ROOT / "testdata" / "acmecrm"
EXPECTED_PATH = DATA / "expected.json"


def _acmecrm_rows() -> dict[str, list[dict[str, str]]]:
    return {
        "customers": _load_rows_from_dir(DATA, "customers.csv"),
        "subscriptions": _load_rows_from_dir(DATA, "subscriptions.csv"),
        "invoices": _load_rows_from_dir(DATA, "invoices.csv"),
        "invoice_line_items": _load_rows_from_dir(DATA, "invoice_line_items.csv"),
        "price_catalog": _load_rows_from_dir(DATA, "price_catalog.csv"),
        "coupons": _load_rows_from_dir(DATA, "coupons.csv"),
    }


def test_acmecrm_csv_round_trip_matches_golden_primary_arr():
    rows = _acmecrm_rows()
    ctx, _id_maps = build_context_from_state(rows)
    findings = []
    for rule in get_all_rules():
        if rule.evaluate:
            findings.extend(rule.evaluate(ctx))

    attributed = attribute_findings(findings)
    primary = sum_primary_recoverable_arr(attributed)
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
    portfolio = expected["portfolio"]
    assert primary >= Decimal(portfolio["primary_recoverable_arr_min"])
    assert primary <= Decimal(portfolio["primary_recoverable_arr_max"])
