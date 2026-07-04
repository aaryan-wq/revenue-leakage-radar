"""Catalog of deterministic verification fixtures, one per rule plus edge cases."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from harness.injections import ALL_RULE_IDS

FixtureType = Literal["minimal", "generated", "negative", "edge", "combined"]


@dataclass(frozen=True)
class FixtureSpec:
    fixture_id: str
    name: str
    description: str
    fixture_type: FixtureType
    target_rules: list[str] = field(default_factory=list)
    seed: int | None = None
    rule_ids: list[str] | None = None
    customer_count: int = 50
    allow_extra_findings: bool = False


def _rule_seed(rule_id: str) -> int:
    return abs(hash(rule_id)) % (2**28)


def _generated_rule_specs() -> list[FixtureSpec]:
    """Fixtures 04–26: one positive injection per rule (excluding minimal-covered rules)."""
    minimal_rules = {"expired_discount", "legacy_pricing", "orphaned_records"}
    specs: list[FixtureSpec] = []
    index = 4
    for rule_id in ALL_RULE_IDS:
        if rule_id in minimal_rules:
            continue
        specs.append(
            FixtureSpec(
                fixture_id=f"{index:02d}_{rule_id}",
                name=rule_id.replace("_", " ").title(),
                description=f"Positive test for {rule_id} via deterministic injection.",
                fixture_type="generated",
                target_rules=[rule_id],
                seed=_rule_seed(rule_id),
                rule_ids=[rule_id],
                customer_count=60,
                allow_extra_findings=False,
            )
        )
        index += 1
    return specs


FIXTURE_CATALOG: list[FixtureSpec] = [
    FixtureSpec(
        fixture_id="01_normal_company",
        name="Normal Company",
        description="Consistent billing, zero expected findings.",
        fixture_type="minimal",
        target_rules=[],
    ),
    FixtureSpec(
        fixture_id="02_expired_discount",
        name="Expired Discount",
        description="$250 MRR / $3,000 ARR, coupon expired, discount still applied.",
        fixture_type="minimal",
        target_rules=["expired_discount"],
    ),
    FixtureSpec(
        fixture_id="03_legacy_pricing",
        name="Legacy Pricing",
        description="$600 MRR / $7,200 ARR, subscription below post-increase catalog.",
        fixture_type="minimal",
        target_rules=["legacy_pricing"],
    ),
    *_generated_rule_specs(),
    FixtureSpec(
        fixture_id="27_negative_all_rules",
        name="Negative Control",
        description="Clean company, no rule should fire.",
        fixture_type="negative",
        target_rules=ALL_RULE_IDS,
    ),
    FixtureSpec(
        fixture_id="28_edge_zero_quantity",
        name="Zero Quantity",
        description="Zero-quantity subscription, no pricing leakage.",
        fixture_type="edge",
        target_rules=[],
    ),
    FixtureSpec(
        fixture_id="29_edge_free_plan",
        name="Free Plan",
        description="Free tier subscription, no leakage.",
        fixture_type="edge",
        target_rules=[],
    ),
    FixtureSpec(
        fixture_id="30_edge_cancelled_clean",
        name="Cancelled Clean",
        description="Cancelled subscription with no post-cancel billing.",
        fixture_type="edge",
        target_rules=["cancelled_subscription_still_billing"],
        allow_extra_findings=True,
    ),
    FixtureSpec(
        fixture_id="31_edge_orphaned_line_item",
        name="Orphaned Line Item",
        description="Line item referencing missing invoice parent.",
        fixture_type="edge",
        target_rules=["orphaned_records"],
    ),
    FixtureSpec(
        fixture_id="32_combined_discount_billing",
        name="Combined Discount + Billing",
        description="Multiple rules injected together for integration coverage.",
        fixture_type="combined",
        target_rules=["discount_stacking", "duplicate_subscription", "invoice_price_mismatch"],
        seed=9999,
        rule_ids=["discount_stacking", "duplicate_subscription", "invoice_price_mismatch"],
        customer_count=80,
        allow_extra_findings=True,
    ),
]


def get_fixture_spec(fixture_id: str) -> FixtureSpec | None:
    return next((spec for spec in FIXTURE_CATALOG if spec.fixture_id == fixture_id), None)


def all_fixture_ids() -> list[str]:
    return [spec.fixture_id for spec in FIXTURE_CATALOG]
