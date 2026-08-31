#!/usr/bin/env python3
"""End-to-end: Nimbus Analytics through estimator + CSV audit."""

from __future__ import annotations

import json
import random
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from calibration.audit_runner import run_audit_on_rows
from estimator.modeling.pipeline import run_model
from harness.company_generator import generate_company
from harness.csv_fuzzer import export_csvs
from harness.types import GroundTruthFinding

COMPANY_NAME = "Nimbus Analytics"
TARGET_ARR = 12_000_000
CUSTOMER_COUNT = 450
SEED = 12_000_042
INJECTED_RULES = [
    "expired_discount",
    "legacy_pricing",
    "invoice_price_mismatch",
    "manual_price_override",
    "duplicate_discount_stacking",
]

NIMBUS_ANSWERS = {
    "profile.company_type": "b2b_saas",
    "profile.arr_amount": TARGET_ARR,
    "profile.arr_confidence": "approximate",
    "profile.customer_count": CUSTOMER_COUNT,
    "pricing.models": ["flat", "per_seat", "custom_enterprise", "addons"],
    "seats.reconciliation": "manual",
    "seats.true_up": False,
    "seats.self_service": True,
    "product.billable_count": "3_5",
    "product.independent_catalogs": "some",
    "product.addons": True,
    "contracts.negotiated_arr_pct": "26_50",
    "contracts.custom_pricing": "yes",
    "contracts.grandfathering": "sometimes",
    "contracts.renewal_increases": "partially",
    "discounts.frequency": "common",
    "discounts.expiry_handling": "manual_finance",
    "discounts.auto_expiry_removal": "rarely",
    "discounts.expiry_confidence": 2,
    "discounts.stacking_policy": "limited",
    "changes.pricing_changes_24mo": "2_3",
    "changes.migration_method": "renewal",
    "systems.billing_system_count": "1",
    "systems.primary_platform": "stripe",
    "operations.manual_override_frequency": "sometimes",
    "operations.manual_change_logging": "partially",
    "operations.unticketed_adjustments": "sometimes",
    "operations.credit_memo_process": "reviewed",
    "operations.churn_billing_cutoff": "within_week",
    "operations.invoice_cadence": "scheduled",
    "operations.customer_dedup": "quarterly",
    "quote_to_bill.commercial_truth": "crm",
    "quote_to_bill.quote_automation": "partial",
    "quote_to_bill.finance_sales_disagreement": "sometimes",
    "migrations.migrated_36mo": False,
    "international.multi_currency": False,
    "controls.finance_team_size": "4_10",
    "controls.billing_owner": True,
    "controls.monthly_reconciliation": "quarterly",
    "controls.billing_qa": "sometimes",
    "controls.invoice_price_qa": "sometimes",
    "controls.revenue_recognition_review": "quarterly",
    "velocity.commercial_changes_12mo": "3_5",
    "confidence.billing_confidence": 3,
    "confidence.last_reconciliation": "3_6mo",
}

MONEY_FIELDS = {
    "price",
    "list_price",
    "unit_price",
    "extended_price",
    "total",
    "subtotal",
    "discount",
    "credit_amount",
    "contract_price",
    "expected_renewal_price",
}


def _fmt(value: float) -> str:
    return f"${value:,.0f}"


def _scale_rows(rows: dict[str, list[dict]], scale: float) -> dict[str, list[dict]]:
    scaled: dict[str, list[dict]] = {}
    for table, items in rows.items():
        scaled[table] = []
        for row in items:
            copy = dict(row)
            for key, value in copy.items():
                if key in MONEY_FIELDS or key.endswith("_price"):
                    try:
                        copy[key] = f"{float(value) * scale:.4f}"
                    except (TypeError, ValueError):
                        pass
            scaled[table].append(copy)
    return scaled


def _scale_ground_truth(findings: list[GroundTruthFinding], scale: Decimal) -> list[GroundTruthFinding]:
    scaled: list[GroundTruthFinding] = []
    for finding in findings:
        if finding.is_negative:
            scaled.append(finding)
            continue
        scaled.append(
            replace(
                finding,
                expected_monthly_leakage=finding.expected_monthly_leakage * scale,
                expected_annual_leakage=finding.expected_annual_leakage * scale,
            )
        )
    return scaled


def _injected_by_rule(findings: list[GroundTruthFinding]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for finding in findings:
        if finding.is_negative:
            continue
        totals[finding.rule_id] = totals.get(finding.rule_id, 0.0) + float(finding.expected_annual_leakage)
    return totals


def main() -> None:
    company = generate_company(
        seed=SEED,
        customer_count=300,
        product_count=4,
        rule_ids=INJECTED_RULES,
        verification_mode=True,
    )
    base_arr = float(company.state.profile.arr_target)
    scale = TARGET_ARR / base_arr if base_arr > 0 else 1.0

    rows = _scale_rows(company.rows(), scale)
    ground_truth = _scale_ground_truth(list(company.ground_truth.findings), Decimal(str(scale)))
    audit = run_audit_on_rows(rows, ground_truth)
    estimator = run_model(NIMBUS_ANSWERS, random_seed=42, scenario="aggressive", include_sensitivity=False)

    out_dir = Path(__file__).resolve().parents[2] / "testdata" / "nimbus_analytics"
    out_dir.mkdir(parents=True, exist_ok=True)
    export_csvs(rows, out_dir / "billing", random.Random(SEED))

    est = estimator["estimate"]
    injected_by_rule = _injected_by_rule(ground_truth)
    report = {
        "company": {
            "name": COMPANY_NAME,
            "arr_usd": TARGET_ARR,
            "customers": CUSTOMER_COUNT,
            "billing_platform": "Stripe",
            "pricing": "Per-seat SaaS with enterprise deals and add-ons",
            "risk_profile": "Manual discount cleanup, grandfathering, partial sales-to-billing automation",
            "seed": SEED,
            "injected_rules": INJECTED_RULES,
            "csv_dir": str(out_dir / "billing"),
        },
        "injected_leakage_annual_usd": audit.injected_annual_leakage,
        "injected_by_rule": injected_by_rule,
        "csv_audit": {
            "primary_recoverable_arr": audit.primary_recoverable_arr,
            "matched_findings": audit.matched_findings,
            "expected_findings": audit.expected_findings,
            "per_rule_arr": audit.per_rule_arr,
        },
        "estimator": {
            "low": est["low"],
            "high": est["high"],
            "central": est["central"],
            "confidence": estimator.get("confidence"),
            "top_hypotheses": [
                {"name": h["name"], "high": h["high"]} for h in estimator.get("top_hypotheses", [])[:5]
            ],
        },
    }
    (out_dir / "e2e_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=" * 72)
    print(f"COMPANY: {COMPANY_NAME}")
    print(f"ARR: {_fmt(TARGET_ARR)} | Customers: {CUSTOMER_COUNT:,}")
    print("Model: B2B SaaS workflow analytics, per-seat on Stripe, enterprise deals, messy discounts")
    print(f"Billing CSVs: {out_dir / 'billing'}")
    print("=" * 72)

    print("\nPLANTED LEAKAGE IN CSVs (ground truth)")
    print(f"  Total: {_fmt(audit.injected_annual_leakage)} /year")
    for rule, amount in sorted(injected_by_rule.items(), key=lambda x: -x[1]):
        print(f"    {rule}: {_fmt(amount)}")

    print("\nCSV AUDIT (deterministic verification on billing exports)")
    print(f"  Primary recoverable ARR: {_fmt(audit.primary_recoverable_arr)}")
    print(f"  Findings matched: {audit.matched_findings}/{audit.expected_findings}")
    for rule, amount in sorted(audit.per_rule_arr.items(), key=lambda x: -x[1]):
        if amount > 0:
            print(f"    {rule}: {_fmt(amount)}")

    print("\nESTIMATOR (questionnaire only, no CSV upload)")
    print(f"  ~{_fmt(est['high'])} /year (aggressive band: {_fmt(est['low'])} to {_fmt(est['high'])})")
    print(f"  Central mean: {_fmt(est['central'])} | Confidence: {estimator.get('confidence')}")
    print("  Top likely sources:")
    for h in estimator.get("top_hypotheses", [])[:5]:
        print(f"    {h['name']}: ~{_fmt(h['high'])}")

    if audit.primary_recoverable_arr > 0:
        gap = (est["high"] - audit.primary_recoverable_arr) / audit.primary_recoverable_arr * 100
        print(f"\nEstimator high vs CSV audit: {gap:+.1f}%")


if __name__ == "__main__":
    main()
