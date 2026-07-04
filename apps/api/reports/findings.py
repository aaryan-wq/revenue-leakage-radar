import json
import uuid
from collections import defaultdict
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from models import Finding
from reports.entity_ids import EntityIdResolver, display_entity_ids
from verification.formatting import (
    format_decimal_display,
    normalize_calculation_trace,
    normalize_evidence_records,
    normalize_leakage_computation,
    normalize_numeric_string,
)
from verification.recoverable import (
    _leakage_semantics,
    _resolve_leakage_computation,
    finding_recoverable_amount,
)
from verification.attribution import sum_primary_recoverable_arr, sum_secondary_excluded_arr
from verification.financial import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM
from verification.registry import RULES, RuleDefinition

CATEGORY_LABELS: dict[str, str] = {
    "discounts": "Expired Discounts",
    "pricing": "Legacy Pricing",
    "renewals": "Renewal Pricing",
    "subscriptions": "Subscription Issues",
    "billing": "Invoice Errors",
    "credits": "Credit Adjustments",
    "overrides": "Manual Overrides",
    "usage": "Usage & Seats",
    "contracts": "Contract Mismatches",
    "monetization": "Monetization Gaps",
}


def rule_lookup() -> dict[str, RuleDefinition]:
    return {rule.rule_id: rule for rule in RULES}


def category_label(category: str) -> str:
    return CATEGORY_LABELS.get(category, category.replace("_", " ").title())


def is_primary_finding(finding: Finding) -> bool:
    return (finding.attribution or "primary") == "primary"


def primary_findings(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings if is_primary_finding(f)]


def parse_evidence(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {"records": []}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"records": []}


def rule_title(finding: Finding) -> str:
    if finding.rule_name:
        return finding.rule_name
    rule = rule_lookup().get(finding.rule_id)
    return rule.name if rule else finding.rule_id.replace("_", " ").title()


def parse_calculation_trace(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def rule_category(rule_id: str) -> str:
    rule = rule_lookup().get(rule_id)
    return rule.category if rule else "other"


def build_primary_finding_lookup(findings: list[Finding]) -> dict[str, Finding]:
    return {
        finding.finding_ref: finding
        for finding in findings
        if finding.finding_ref and is_primary_finding(finding)
    }


def serialize_finding(
    finding: Finding,
    *,
    include_evidence: bool = True,
    evidence_record_limit: int | None = None,
    entity_resolver: EntityIdResolver | None = None,
    primary_by_ref: dict[str, Finding] | None = None,
) -> dict[str, Any]:
    evidence = parse_evidence(finding.evidence)
    customer_id, subscription_id, invoice_id = display_entity_ids(
        finding,
        evidence,
        entity_resolver,
    )
    payload: dict[str, Any] = {
        "id": str(finding.id),
        "rule_id": finding.rule_id,
        "title": rule_title(finding),
        "category": rule_category(finding.rule_id),
        "category_label": category_label(rule_category(finding.rule_id)),
        "severity": finding.severity,
        "confidence": format_decimal_display(finding.confidence) or str(finding.confidence),
        "customer_id": customer_id,
        "subscription_id": subscription_id,
        "invoice_id": invoice_id,
        "estimated_monthly_loss": format_decimal_display(finding.estimated_monthly_loss)
        or str(finding.estimated_monthly_loss),
        "estimated_arr_loss": format_decimal_display(finding.estimated_arr_loss)
        or str(finding.estimated_arr_loss),
        "recommendation": finding.recommendation,
        "attribution": finding.attribution or "primary",
        "leak_family": finding.leak_family,
        "finding_ref": finding.finding_ref,
        "primary_finding_ref": finding.primary_finding_ref,
    }
    if finding.attribution == "secondary" and finding.primary_finding_ref and primary_by_ref:
        primary = primary_by_ref.get(finding.primary_finding_ref)
        if primary:
            payload["primary_finding_id"] = str(primary.id)
            payload["primary_finding_title"] = rule_title(primary)
    computation = evidence.get("leakage_computation")
    if computation:
        payload["leakage_computation"] = normalize_leakage_computation(computation)
    semantics = _leakage_semantics(computation or _resolve_leakage_computation(finding))
    if semantics:
        payload["leakage_semantics"] = semantics
    recoverable = finding_recoverable_amount(finding).quantize(Decimal("0.01"))
    payload["recoverable_amount"] = format_decimal_display(recoverable) or str(recoverable)
    trace = parse_calculation_trace(finding.calculation_trace) or evidence.get("calculation_trace")
    if trace:
        payload["calculation_trace"] = normalize_calculation_trace(trace)
    if include_evidence:
        records = normalize_evidence_records(evidence.get("records", []))
        if evidence_record_limit is not None:
            records = records[:evidence_record_limit]
            payload["evidence_records"] = records
        else:
            evidence_payload = dict(evidence)
            evidence_payload["records"] = records
            payload["evidence"] = evidence_payload
            payload["evidence_records"] = records
    return payload


def group_findings_by_category(findings: list[Finding]) -> dict[str, list[Finding]]:
    grouped: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        grouped[rule_category(finding.rule_id)].append(finding)
    return dict(grouped)


def build_opportunity_breakdown(findings: list[Finding]) -> list[dict[str, Any]]:
    grouped = group_findings_by_category(primary_findings(findings))
    breakdown: list[dict[str, Any]] = []

    for category, items in grouped.items():
        arr = sum((finding_recoverable_amount(f) for f in items), Decimal("0"))
        conf = _category_confidence(items)
        breakdown.append(
            {
                "category": category,
                "label": category_label(category),
                "arr": str(arr.quantize(Decimal("0.01"))),
                "confidence": str(conf) if conf is not None else None,
                "issue_count": len(items),
                "account_count": len({f.customer_id for f in items if f.customer_id}),
            }
        )

    breakdown.sort(key=lambda row: Decimal(row["arr"]), reverse=True)
    return breakdown


def build_reconciliation(findings: list[Finding], recoverable_arr: Decimal | str) -> dict[str, str | int]:
    primary = primary_findings(findings)
    secondary_excluded = sum_secondary_excluded_arr(findings)
    raw_sum = sum((f.estimated_arr_loss for f in findings), Decimal("0"))
    primary_total = sum_primary_recoverable_arr(findings)
    return {
        "total_findings": len(findings),
        "primary_findings": len(primary),
        "secondary_findings": len(findings) - len(primary),
        "primary_recoverable_arr": str(primary_total.quantize(Decimal("0.01"))),
        "secondary_excluded_arr": str(secondary_excluded.quantize(Decimal("0.01"))),
        "raw_sum_arr": str(raw_sum.quantize(Decimal("0.01"))),
        "headline_recoverable_arr": str(Decimal(str(recoverable_arr)).quantize(Decimal("0.01"))),
    }


def build_locked_preview(findings: list[Finding], limit: int = 3) -> list[dict[str, Any]]:
    sorted_findings = sorted(
        primary_findings(findings),
        key=finding_recoverable_amount,
        reverse=True,
    )
    preview: list[dict[str, Any]] = []
    for finding in sorted_findings[:limit]:
        preview.append(
            {
                "title": rule_title(finding),
                "category": rule_category(finding.rule_id),
                "category_label": category_label(rule_category(finding.rule_id)),
                "arr": str(finding_recoverable_amount(finding).quantize(Decimal("0.01"))),
            }
        )
    return preview


def confidence_band(confidence: Decimal | None) -> str:
    if confidence is None:
        return "medium"
    if confidence >= CONFIDENCE_HIGH:
        return "high"
    if confidence >= CONFIDENCE_MEDIUM:
        return "medium"
    return "low"


def sum_arr_by_confidence_band(findings: list[Finding]) -> dict[str, str]:
    high = Decimal("0")
    medium = Decimal("0")
    low = Decimal("0")
    for finding in primary_findings(findings):
        band = confidence_band(finding.confidence)
        amount = finding_recoverable_amount(finding)
        if band == "high":
            high += amount
        elif band == "medium":
            medium += amount
        else:
            low += amount
    return {
        "high": str(high.quantize(Decimal("0.01"))),
        "medium": str(medium.quantize(Decimal("0.01"))),
        "low": str(low.quantize(Decimal("0.01"))),
    }


def _category_confidence(items: list[Finding]) -> Decimal | None:
    if not items:
        return None
    total_weight = Decimal("0")
    weighted_sum = Decimal("0")
    for item in items:
        weight = finding_recoverable_amount(item)
        if weight > 0:
            weighted_sum += item.confidence * weight
            total_weight += weight
    if total_weight == 0:
        return items[0].confidence
    return (weighted_sum / total_weight).quantize(Decimal("0.01"))


def get_finding_by_id(db: Session, finding_id: uuid.UUID) -> Finding | None:
    return db.query(Finding).filter(Finding.id == finding_id).first()
