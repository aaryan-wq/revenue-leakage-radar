"""Backward-compatible registry shim for coverage and legacy imports."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from core.canonical_entities import CanonicalEntity
from verification.context import CanonicalContext
from verification.eligibility.schema import FieldRequirement, RuleSpec
from verification.engine.registry import ALL_RULE_MODULES, get_all_rules as get_all_rule_modules
from verification.types import RuleFinding


@dataclass
class RuleDefinition:
    rule_id: str
    name: str
    category: str
    required_entities: frozenset[CanonicalEntity] = field(default_factory=frozenset)
    optimal_entities: frozenset[CanonicalEntity] = field(default_factory=frozenset)
    requires_credit_data: bool = False
    requires_manual_override: bool = False
    evaluate: Callable[[CanonicalContext], list[RuleFinding]] | None = None


FIELD_ENTITY_MAP: dict[CanonicalEntity, set[str]] = {
    CanonicalEntity.CUSTOMER: {"customer_id", "name"},
    CanonicalEntity.SUBSCRIPTION: {
        "subscription_id",
        "customer_id",
        "product_id",
        "price",
        "quantity",
        "billing_interval",
        "status",
        "coupon_id",
        "currency",
        "start_date",
        "renewal_date",
    },
    CanonicalEntity.INVOICE: {
        "invoice_id",
        "customer_id",
        "subscription_id",
        "invoice_date",
        "discount",
        "total",
        "currency",
        "credit_amount",
        "period_start",
        "period_end",
    },
    CanonicalEntity.INVOICE_LINE_ITEM: {
        "line_item_id",
        "invoice_id",
        "subscription_id",
        "product_id",
        "unit_price",
        "quantity",
        "billing_interval",
        "is_manual_override",
        "sku",
    },
    CanonicalEntity.PRICE: {
        "product_id",
        "list_price",
        "effective_date",
        "billing_interval",
        "currency",
        "sku",
    },
    CanonicalEntity.COUPON: {"coupon_id", "code", "expires_at", "discount_type", "discount_value", "active"},
    CanonicalEntity.CONTRACT: {
        "contract_id",
        "customer_id",
        "contract_price",
        "price_increase_date",
        "expected_renewal_price",
        "end_date",
    },
    CanonicalEntity.ACCOUNT: {"account_id", "customer_id", "seat_count"},
}


def _entities_from_fields(fields: list[FieldRequirement]) -> frozenset[CanonicalEntity]:
    return frozenset(field.entity for field in fields)


def _rule_definition_from_spec(module) -> RuleDefinition:
    spec: RuleSpec = module.spec
    required_entities = _entities_from_fields(spec.required_fields)
    optimal_entities = _entities_from_fields(spec.optional_fields)
    requires_credit = spec.rule_id in {"credit_leakage", "duplicate_credit"}
    requires_manual = spec.rule_id == "manual_price_override"

    def evaluate(ctx: CanonicalContext) -> list[RuleFinding]:
        from verification.findings.generator import FindingGenerator

        results = module.evaluate(ctx)
        return [
            FindingGenerator.from_rule_result(spec, result, audit_id=ctx.audit_id)
            for result in results
        ]

    return RuleDefinition(
        rule_id=spec.rule_id,
        name=spec.name,
        category=spec.category,
        required_entities=required_entities,
        optimal_entities=optimal_entities,
        requires_credit_data=requires_credit,
        requires_manual_override=requires_manual,
        evaluate=evaluate,
    )


RULES: list[RuleDefinition] = [_rule_definition_from_spec(module) for module in ALL_RULE_MODULES]


def get_all_rules() -> list[RuleDefinition]:
    return list(RULES)
