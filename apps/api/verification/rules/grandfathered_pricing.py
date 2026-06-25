from datetime import datetime, timezone
from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "grandfathered_without_contract"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    now = datetime.now(timezone.utc)

    for sub in ctx.subscriptions:
        if not sub.product_id or not sub.price or not sub.start_date:
            continue
        if sub.status and sub.status.lower() not in ("active", "trialing"):
            continue

        catalog = ctx.latest_catalog_version(sub.product_id)
        if not catalog or not catalog.list_price or sub.price >= catalog.list_price:
            continue

        contracts = ctx.contracts_for_customer(sub.customer_id)
        if ctx.has_crm and contracts:
            has_exception = any(
                c.contract_price is not None and c.contract_price < catalog.list_price
                for c in contracts
            )
            if has_exception:
                continue

        age_days = (now - sub.start_date.replace(tzinfo=timezone.utc)).days if sub.start_date else 0
        if age_days < 365 and not ctx.has_crm:
            continue

        monthly, annual = compute_leakage(
            catalog.list_price, sub.price, sub.quantity or 1, sub.billing_interval
        )
        conf = CONFIDENCE_HIGH if ctx.has_crm else CONFIDENCE_MEDIUM

        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Grandfathered pricing without contract exception",
                severity="medium",
                confidence=conf,
                customer_id=str(sub.customer_id),
                subscription_id=str(sub.id),
                expected_value=catalog.list_price,
                actual_value=sub.price,
                delta=catalog.list_price - sub.price,
                estimated_monthly_loss=monthly,
                estimated_arr_loss=annual,
                recommendation="Validate whether legacy pricing is contractually approved.",
                evidence=[
                    EvidenceRecord(
                        field="grandfathered_price",
                        expected=str(catalog.list_price),
                        actual=str(sub.price),
                        reference_ids={"product_id": sub.product_id or ""},
                    )
                ],
            )
        )

    return findings
