from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "legacy_pricing_pre_catalog"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    for sub in ctx.subscriptions:
        if not sub.product_id or not sub.price or not sub.start_date:
            continue
        if sub.status and sub.status.lower() not in ("active", "trialing"):
            continue

        catalog = ctx.catalog_for_product(sub.product_id, as_of=sub.start_date)
        if not catalog or not catalog.list_price:
            continue
        if not catalog.effective_date or catalog.effective_date <= sub.start_date:
            continue
        if sub.price >= catalog.list_price:
            continue

        monthly, annual = compute_leakage(
            catalog.list_price, sub.price, sub.quantity or 1, sub.billing_interval
        )
        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Legacy pricing below current catalog",
                severity="medium",
                confidence=CONFIDENCE_HIGH,
                customer_id=str(sub.customer_id),
                subscription_id=str(sub.id),
                expected_value=catalog.list_price,
                actual_value=sub.price,
                delta=catalog.list_price - sub.price,
                estimated_monthly_loss=monthly,
                estimated_arr_loss=annual,
                recommendation="Review subscription for grandfathered pricing and align to current catalog.",
                evidence=[
                    EvidenceRecord(
                        field="subscription_price",
                        expected=str(catalog.list_price),
                        actual=str(sub.price),
                        reference_ids={"product_id": sub.product_id or ""},
                    )
                ],
            )
        )

    return findings
