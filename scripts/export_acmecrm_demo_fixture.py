#!/usr/bin/env python3
"""Export AcmeCRM verification output as a frontend demo fixture JSON."""

from __future__ import annotations

import json
import sys
import uuid
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "apps" / "api"))

from compare_acmecrm_leakage import build_context  # noqa: E402
from reports.findings import (  # noqa: E402
    build_opportunity_breakdown,
    build_reconciliation,
    category_label,
    primary_findings,
    rule_category,
    rule_lookup,
)
from verification.attribution import (  # noqa: E402
    attribute_findings,
    sum_primary_recoverable_arr,
)
from verification.formatting import (  # noqa: E402
    format_decimal_display,
    normalize_calculation_trace,
    normalize_evidence_records,
    normalize_leakage_computation,
)
from verification.recoverable import finding_recoverable_amount  # noqa: E402
from verification.registry import get_all_rules  # noqa: E402
from verification.types import RuleFinding  # noqa: E402

OUTPUT_PATH = ROOT / "apps" / "web" / "lib" / "demo" / "acmecrm-demo.fixture.json"

DEMO_AUDIT_ID = "00000000-0000-4000-a000-000000000001"
DEMO_REPORT_ID = "00000000-0000-4000-a000-000000000002"

SLUG_BY_RULE: dict[str, str] = {
    "expired_discount": "expired-discount-still-applied",
    "incorrect_addon_price": "legacy-pricing-after-renewal",
    "invoice_price_mismatch": "invoice-line-item-mismatch",
    "discount_stacking": "duplicate-discount-stacking",
    "grandfathered_pricing": "undercharged-subscriptions",
    "price_catalog_mismatch": "price-catalog-mismatch",
    "renewal_price_drift": "renewal-price-drift",
}


def _stable_finding_id(slug: str, index: int) -> str:
    namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
    return str(uuid.uuid5(namespace, f"demo-finding:{slug}:{index}"))


def _rule_finding_arr(finding: RuleFinding) -> Decimal:
    if finding.attribution != "primary":
        return finding.estimated_arr_loss
    if finding.leakage_computation is not None:
        return finding.leakage_computation.annual_loss
    return finding.estimated_arr_loss


def serialize_rule_finding(
    finding: RuleFinding,
    *,
    finding_id: str,
    primary_by_ref: dict[str, RuleFinding],
) -> dict:
    evidence_json = finding.evidence_json()
    records = normalize_evidence_records(evidence_json.get("records", []))
    category = rule_category(finding.rule_id)
    recoverable = _rule_finding_arr(finding).quantize(Decimal("0.01"))

    payload: dict = {
        "id": finding_id,
        "rule_id": finding.rule_id,
        "title": finding.title or finding.rule_name,
        "category": category,
        "category_label": category_label(category),
        "severity": finding.severity,
        "confidence": format_decimal_display(finding.confidence) or str(finding.confidence),
        "customer_id": finding.customer_id,
        "subscription_id": finding.subscription_id,
        "invoice_id": finding.invoice_id,
        "estimated_monthly_loss": format_decimal_display(finding.estimated_monthly_loss)
        or str(finding.estimated_monthly_loss),
        "estimated_arr_loss": format_decimal_display(finding.estimated_arr_loss)
        or str(finding.estimated_arr_loss),
        "recommendation": finding.recommendation,
        "attribution": finding.attribution or "primary",
        "leak_family": finding.leak_family,
        "finding_ref": finding.finding_ref,
        "primary_finding_ref": finding.primary_finding_ref,
        "recoverable_amount": format_decimal_display(recoverable) or str(recoverable),
        "evidence_records": records,
        "evidence": {**evidence_json, "records": records},
    }

    if finding.leakage_computation is not None:
        payload["leakage_computation"] = normalize_leakage_computation(
            finding.leakage_computation.model_dump(mode="json")
        )
        payload["leakage_semantics"] = finding.leakage_computation.semantics

    if finding.calculation_trace is not None:
        payload["calculation_trace"] = normalize_calculation_trace(
            finding.calculation_trace.model_dump(mode="json")
        )
    elif evidence_json.get("calculation_trace"):
        payload["calculation_trace"] = normalize_calculation_trace(evidence_json["calculation_trace"])

    if finding.attribution == "secondary" and finding.primary_finding_ref:
        primary = primary_by_ref.get(finding.primary_finding_ref)
        if primary:
            payload["primary_finding_title"] = primary.title or primary.rule_name

    return payload


def _confidence_band(findings: list[RuleFinding]) -> dict[str, str]:
    from verification.financial import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM

    bands = {"high": Decimal("0"), "medium": Decimal("0"), "low": Decimal("0")}
    for finding in primary_findings_rule(findings):
        amount = _rule_finding_arr(finding)
        conf = finding.confidence
        if conf >= CONFIDENCE_HIGH:
            bands["high"] += amount
        elif conf >= CONFIDENCE_MEDIUM:
            bands["medium"] += amount
        else:
            bands["low"] += amount
    return {key: str(value.quantize(Decimal("0.01"))) for key, value in bands.items()}


def primary_findings_rule(findings: list[RuleFinding]) -> list[RuleFinding]:
    return [f for f in findings if (f.attribution or "primary") == "primary"]


def _weighted_confidence(findings: list[RuleFinding]) -> str | None:
    primaries = primary_findings_rule(findings)
    if not primaries:
        return None
    total_arr = sum(_rule_finding_arr(f) for f in primaries)
    if total_arr <= 0:
        return None
    weighted = sum(_rule_finding_arr(f) * f.confidence for f in primaries) / total_arr
    return str(weighted.quantize(Decimal("0.01")))


def _select_demo_findings(findings: list[RuleFinding], limit: int = 12) -> list[RuleFinding]:
    """Pick representative findings: top primaries plus a few secondary overlaps."""
    sorted_findings = sorted(findings, key=_rule_finding_arr, reverse=True)
    selected: list[RuleFinding] = []
    seen_rules: set[str] = set()

    for finding in sorted_findings:
        if finding.attribution != "primary":
            continue
        if finding.rule_id in seen_rules and len(selected) >= 6:
            continue
        selected.append(finding)
        seen_rules.add(finding.rule_id)
        if len(selected) >= limit - 3:
            break

    for finding in sorted_findings:
        if finding.attribution != "secondary":
            continue
        selected.append(finding)
        if len(selected) >= limit:
            break

    while len(selected) < limit:
        for finding in sorted_findings:
            if finding not in selected:
                selected.append(finding)
            if len(selected) >= limit:
                break
        break

    return selected[:limit]


def _slug_for_finding(finding: RuleFinding, index: int) -> str:
    base = SLUG_BY_RULE.get(finding.rule_id, finding.rule_id.replace("_", "-"))
    if finding.subscription_id:
        return f"{base}-{finding.subscription_id.lower()}"
    return f"{base}-{index}"


def _rule_finding_to_orm(audit_id: uuid.UUID, finding: RuleFinding) -> object:
    from models import Finding

    return Finding(
        id=uuid.uuid4(),
        audit_id=audit_id,
        rule_id=finding.rule_id,
        rule_name=finding.rule_name,
        severity=finding.severity,
        confidence=finding.confidence,
        status=finding.status,
        customer_id=None,
        invoice_id=None,
        subscription_id=None,
        product_id=finding.product_id,
        expected_value=finding.expected_value,
        actual_value=finding.actual_value,
        difference=finding.delta,
        estimated_monthly_loss=finding.estimated_monthly_loss,
        estimated_arr_loss=finding.estimated_arr_loss,
        recommendation=finding.recommendation,
        evidence=json.dumps(finding.evidence_json()),
        calculation_trace=json.dumps(
            finding.calculation_trace.model_dump(mode="json")
        )
        if finding.calculation_trace
        else None,
        leak_family=finding.leak_family,
        attribution=finding.attribution or "primary",
        primary_finding_ref=finding.primary_finding_ref,
        finding_ref=finding.finding_ref,
        rule_version=finding.rule_version,
    )


def build_fixture() -> dict:
    ctx = build_context()
    raw_findings: list[RuleFinding] = []
    for rule in get_all_rules():
        if rule.evaluate:
            raw_findings.extend(rule.evaluate(ctx))

    attributed = attribute_findings(raw_findings)
    primary_total = sum_primary_recoverable_arr(attributed)
    demo_subset = _select_demo_findings(attributed)

    audit_id = uuid.UUID(DEMO_AUDIT_ID)
    orm_findings = [_rule_finding_to_orm(audit_id, f) for f in attributed]
    confidence_bands = _confidence_band(attributed)
    reconciliation = build_reconciliation(orm_findings, primary_total)
    opportunity_breakdown = build_opportunity_breakdown(orm_findings)

    primary_by_ref = {
        f.finding_ref: f for f in attributed if f.finding_ref and f.attribution == "primary"
    }

    serialized_findings: list[dict] = []
    slugs: dict[str, str] = {}
    for index, finding in enumerate(demo_subset):
        slug = _slug_for_finding(finding, index)
        finding_id = _stable_finding_id(slug, index)
        slugs[slug] = finding_id
        serialized = serialize_rule_finding(
            finding,
            finding_id=finding_id,
            primary_by_ref=primary_by_ref,
        )
        serialized["slug"] = slug
        serialized_findings.append(serialized)

    finding_details: dict[str, dict] = {}
    for item in serialized_findings:
        slug = item.pop("slug")
        finding_details[slug] = {
            **item,
            "audit_id": DEMO_AUDIT_ID,
            "report_id": DEMO_REPORT_ID,
        }

    accounts = len({row["customer_id"] for row in ctx.customers if hasattr(ctx, "customers")})
    invoices = len(getattr(ctx, "invoices", []) or [])

    narrative = (
        f"AcmeCRM's billing exports reveal {reconciliation['primary_findings']} primary revenue "
        f"leakage findings totaling {reconciliation['primary_recoverable_arr']} in recoverable ARR. "
        "The largest concentrations are expired promotional discounts still billing, legacy catalog "
        "pricing after renewal, and invoice execution drift. Each finding includes subscription-level "
        "evidence and a recommended remediation path."
    )

    return {
        "report": {
            "id": DEMO_REPORT_ID,
            "audit_id": DEMO_AUDIT_ID,
            "purchased": True,
            "generated_at": "2025-06-01T00:00:00+00:00",
            "company_name": "AcmeCRM",
            "executive_summary": {
                "recoverable_arr": reconciliation["headline_recoverable_arr"],
                "high_confidence_arr": confidence_bands["high"],
                "medium_confidence_arr": confidence_bands["medium"],
                "low_confidence_arr": confidence_bands["low"],
                "accounts_reviewed": accounts or 300,
                "invoices_reviewed": invoices or 4470,
                "finding_count": reconciliation["total_findings"],
                "confidence": _weighted_confidence(attributed),
                "rules_completed": len(get_all_rules()),
                "rules_total": len(get_all_rules()),
                "narrative": narrative,
                "reconciliation": reconciliation,
            },
            "opportunity_breakdown": opportunity_breakdown,
            "verification_checks": [],
            "findings_total": reconciliation["total_findings"],
            "locked_preview": [],
        },
        "findings": serialized_findings,
        "finding_details": finding_details,
        "slugs": slugs,
    }


def main() -> None:
    fixture = build_fixture()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(fixture, indent=2), encoding="utf-8")
    print(f"Wrote demo fixture to {OUTPUT_PATH}")
    print(f"Primary recoverable ARR: {fixture['report']['executive_summary']['recoverable_arr']}")
    print(f"Demo findings exported: {len(fixture['findings'])}")


if __name__ == "__main__":
    main()
