"""Rule and entity coverage analysis for adaptive audits."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from core.canonical_entities import (
    CanonicalEntity,
    ENTITY_LABELS,
    SOURCE_FILE_TYPE_TO_ENTITIES,
    entities_from_uploaded_files,
)
from core.data_tiers import missing_entities
from core.enums import FileType

FILE_TYPE_LABELS: dict[FileType, str] = {
    FileType.CUSTOMERS: "Customers",
    FileType.SUBSCRIPTIONS: "Subscriptions",
    FileType.INVOICES: "Invoices",
    FileType.INVOICE_LINE_ITEMS: "Invoice Line Items",
    FileType.COUPONS: "Coupons",
    FileType.PRICE_CATALOG: "Prices",
    FileType.CRM_ACCOUNTS: "CRM Accounts",
    FileType.CRM_OPPORTUNITIES: "CRM Opportunities",
    FileType.CRM_CONTRACTS: "CRM Contracts",
}
from verification.context import AuditContext
from verification.registry import RuleDefinition, get_all_rules

BILLING_ENTITY_LABELS: dict[CanonicalEntity, str] = {
    CanonicalEntity.CUSTOMER: "Customers",
    CanonicalEntity.SUBSCRIPTION: "Subscriptions",
    CanonicalEntity.PRICE: "Prices",
    CanonicalEntity.INVOICE: "Invoices",
    CanonicalEntity.INVOICE_LINE_ITEM: "Invoice Line Items",
    CanonicalEntity.COUPON: "Coupons",
    CanonicalEntity.CONTRACT: "Contracts",
}

COVERAGE_SCORE_BUCKETS: dict[str, frozenset[str]] = {
    "pricing": frozenset(
        {
            "legacy_pricing",
            "price_catalog_mismatch",
            "grandfathered_pricing",
            "missing_scheduled_increase",
            "manual_price_override",
            "incorrect_seat_price",
            "incorrect_addon_price",
        }
    ),
    "renewals": frozenset({"renewal_price_drift"}),
    "discounts": frozenset(
        {
            "expired_discount",
            "discount_stacking",
            "duplicate_discount",
            "permanent_promotional_discount",
            "excessive_discount",
            "discount_wrong_product",
        }
    ),
    "credits": frozenset({"credit_leakage", "duplicate_credit"}),
    "invoices": frozenset(
        {
            "invoice_price_mismatch",
            "duplicate_subscription",
            "billing_frequency_mismatch",
            "active_subscription_not_billing",
            "manual_price_override",
            "cancelled_subscription_still_billing",
            "missing_expected_invoice",
        }
    ),
    "contracts": frozenset(
        {
            "grandfathered_pricing",
            "missing_scheduled_increase",
            "permanent_promotional_discount",
            "incorrect_seat_price",
        }
    ),
    "data_quality": frozenset(
        {
            "duplicate_customer",
            "currency_mismatch",
            "orphaned_records",
        }
    ),
}

COVERAGE_BUCKET_LABELS: dict[str, str] = {
    "overall": "Overall",
    "pricing": "Pricing",
    "renewals": "Renewals",
    "discounts": "Discounts",
    "credits": "Credits",
    "invoices": "Invoices",
    "contracts": "Contracts",
    "data_quality": "Data quality",
}

PARTIAL_RULE_WEIGHT = Decimal("0.85")
RAN_RULE_WEIGHT = Decimal("1.0")


@dataclass(frozen=True)
class RuleAvailability:
    rule_id: str
    name: str
    category: str
    status: str
    reason: str | None


def _friendly_skip_reason(
    rule: RuleDefinition,
    missing_required: set[CanonicalEntity],
    *,
    requires_credit: bool,
    requires_manual_override: bool,
) -> str:
    if requires_credit and rule.requires_credit_data:
        return "Missing credit data"
    if requires_manual_override and rule.requires_manual_override:
        return "No manual override flags in line items"
    if missing_required:
        labels = [BILLING_ENTITY_LABELS.get(entity, ENTITY_LABELS.get(entity, entity.value)) for entity in sorted(missing_required, key=lambda e: e.value)]
        if len(labels) == 1:
            entity = next(iter(missing_required))
            if entity == CanonicalEntity.COUPON:
                return "No coupon data"
            if entity == CanonicalEntity.INVOICE:
                return "No invoice-level pricing"
            if entity == CanonicalEntity.INVOICE_LINE_ITEM:
                return "No invoice line item data"
            if entity == CanonicalEntity.CONTRACT:
                return "No contract data"
            return f"No {labels[0].lower()} data"
        return f"Missing {', '.join(labels)}"
    return "Insufficient data for this check"


def resolve_rule_availability(
    rule: RuleDefinition,
    available_entities: set[CanonicalEntity],
    *,
    has_credit_data: bool = False,
    has_manual_override_data: bool = False,
    preview_mode: bool = False,
) -> RuleAvailability:
    if rule.evaluate is None:
        return RuleAvailability(rule.rule_id, rule.name, rule.category, "skipped", "Check not configured")

    missing_required = missing_entities(available_entities, rule.required_entities)
    if missing_required:
        return RuleAvailability(
            rule.rule_id,
            rule.name,
            rule.category,
            "skipped",
            _friendly_skip_reason(rule, missing_required, requires_credit=False, requires_manual_override=False),
        )

    if rule.requires_credit_data and not has_credit_data:
        if preview_mode:
            return RuleAvailability(rule.rule_id, rule.name, rule.category, "partial", None)
        return RuleAvailability(
            rule.rule_id,
            rule.name,
            rule.category,
            "skipped",
            _friendly_skip_reason(rule, set(), requires_credit=True, requires_manual_override=False),
        )

    if rule.requires_manual_override and not has_manual_override_data:
        if preview_mode:
            return RuleAvailability(rule.rule_id, rule.name, rule.category, "partial", None)
        return RuleAvailability(
            rule.rule_id,
            rule.name,
            rule.category,
            "skipped",
            _friendly_skip_reason(rule, set(), requires_credit=False, requires_manual_override=True),
        )

    missing_optimal = missing_entities(available_entities, rule.optimal_entities)
    if missing_optimal:
        return RuleAvailability(rule.rule_id, rule.name, rule.category, "partial", None)

    return RuleAvailability(rule.rule_id, rule.name, rule.category, "available", None)


def _rule_weight(status: str) -> Decimal:
    if status in ("available", "ran"):
        return RAN_RULE_WEIGHT
    if status == "partial":
        return PARTIAL_RULE_WEIGHT
    return Decimal("0")


def _score_percent(rules: list[RuleAvailability]) -> int:
    if not rules:
        return 0
    total = Decimal(len(rules))
    weighted = sum(_rule_weight(rule.status) for rule in rules)
    pct = (weighted / total * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(pct)


def _bucket_rules(all_rules: list[RuleAvailability], bucket_rule_ids: frozenset[str]) -> list[RuleAvailability]:
    return [rule for rule in all_rules if rule.rule_id in bucket_rule_ids]


def _billing_entities_present(available: set[CanonicalEntity]) -> list[str]:
    billing_entities = {
        CanonicalEntity.CUSTOMER,
        CanonicalEntity.SUBSCRIPTION,
        CanonicalEntity.PRICE,
        CanonicalEntity.INVOICE,
        CanonicalEntity.INVOICE_LINE_ITEM,
        CanonicalEntity.COUPON,
        CanonicalEntity.CONTRACT,
    }
    return sorted(
        (BILLING_ENTITY_LABELS.get(entity, ENTITY_LABELS.get(entity, entity.value)) for entity in available if entity in billing_entities),
        key=str,
    )


def _unlock_file_hints(
    skipped_rules: list[RuleAvailability],
    uploaded_types: set[FileType],
) -> list[dict[str, Any]]:
    """Suggest file uploads that unlock the most skipped rules."""
    file_unlock_counts: dict[FileType, set[str]] = {}
    for rule in skipped_rules:
        for file_type, entities in SOURCE_FILE_TYPE_TO_ENTITIES.items():
            if file_type in uploaded_types:
                continue
            hypothetical = entities_from_uploaded_files(uploaded_types | {file_type})
            refreshed = resolve_rule_availability(
                next(r for r in get_all_rules() if r.rule_id == rule.rule_id),
                hypothetical,
            )
            if refreshed.status != "skipped":
                file_unlock_counts.setdefault(file_type, set()).add(rule.rule_id)

    hints = [
        {
            "file_type": file_type.value,
            "label": FILE_TYPE_LABELS.get(file_type, file_type.value.replace("_", " ").title()),
            "rules_unlocked": len(rule_ids),
        }
        for file_type, rule_ids in file_unlock_counts.items()
    ]
    return sorted(hints, key=lambda item: (-item["rules_unlocked"], item["file_type"]))


def analyze_coverage(
    *,
    available_entities: set[CanonicalEntity],
    uploaded_file_types: set[FileType] | None = None,
    has_credit_data: bool = False,
    has_manual_override_data: bool = False,
    preview_mode: bool = False,
) -> dict[str, Any]:
    uploaded_types = uploaded_file_types or set()
    all_rules = get_all_rules()
    availabilities = [
        resolve_rule_availability(
            rule,
            available_entities,
            has_credit_data=has_credit_data,
            has_manual_override_data=has_manual_override_data,
            preview_mode=preview_mode,
        )
        for rule in all_rules
    ]

    runnable = [rule for rule in availabilities if rule.status in ("available", "partial")]
    skipped = [rule for rule in availabilities if rule.status == "skipped"]

    category_scores = {
        bucket: _score_percent(_bucket_rules(availabilities, rule_ids))
        for bucket, rule_ids in COVERAGE_SCORE_BUCKETS.items()
    }
    category_scores["overall"] = _score_percent(availabilities)

    return {
        "billing_data_received": _billing_entities_present(available_entities),
        "rules_available": len(runnable),
        "rules_total": len(all_rules),
        "available_rules": [
            {
                "name": rule.name,
                "status": rule.status,
                "note": "Reduced coverage" if rule.status == "partial" else None,
            }
            for rule in runnable
        ],
        "unavailable_rules": [
            {"name": rule.name, "reason": rule.reason or "Insufficient data"}
            for rule in skipped
        ],
        "estimated_confidence": category_scores["overall"],
        "category_scores": [
            {"category": bucket, "label": COVERAGE_BUCKET_LABELS[bucket], "score": category_scores[bucket]}
            for bucket in (
                "overall",
                "pricing",
                "renewals",
                "discounts",
                "credits",
                "invoices",
                "contracts",
                "data_quality",
            )
        ],
        "unlock_hints": _unlock_file_hints(skipped, uploaded_types),
    }


def analyze_coverage_from_context(ctx: AuditContext) -> dict[str, Any]:
    return analyze_coverage(
        available_entities=ctx.available_entities_set(),
        uploaded_file_types=ctx.uploaded_file_types,
        has_credit_data=ctx.has_credit_data,
        has_manual_override_data=ctx.has_manual_override_data,
    )
