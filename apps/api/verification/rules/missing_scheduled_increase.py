from datetime import datetime, timezone
from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "missing_scheduled_increase"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    now = datetime.now(timezone.utc)

    if ctx.has_crm:
        for contract in ctx.crm_contracts:
            if not contract.price_increase_date or not contract.customer_id:
                continue
            inc_date = contract.price_increase_date
            if inc_date.tzinfo is None:
                inc_date = inc_date.replace(tzinfo=timezone.utc)
            if inc_date > now:
                continue

            subs = ctx.subscriptions_for_customer(contract.customer_id)
            for sub in subs:
                if not sub.price or not contract.contract_price:
                    continue
                if sub.price > contract.contract_price:
                    continue
                expected = contract.contract_price
                monthly, annual = compute_leakage(
                    expected, sub.price, sub.quantity or 1, sub.billing_interval
                )
                findings.append(
                    RuleFinding(
                        rule_id=RULE_ID,
                        title="Missing scheduled price increase",
                        severity="high",
                        confidence=CONFIDENCE_HIGH,
                        customer_id=str(sub.customer_id),
                        subscription_id=str(sub.id),
                        expected_value=expected,
                        actual_value=sub.price,
                        delta=expected - sub.price,
                        estimated_monthly_loss=monthly,
                        estimated_arr_loss=annual,
                        recommendation="Apply contracted price increase that was scheduled but not reflected in billing.",
                        evidence=[
                            EvidenceRecord(
                                field="price_increase_date",
                                expected=str(inc_date.date()),
                                actual=str(sub.price),
                                reference_ids={"contract": contract.external_contract_id},
                            )
                        ],
                    )
                )
        return findings

    for sub in ctx.subscriptions:
        if not sub.renewal_date or not sub.price:
            continue
        renewal = sub.renewal_date
        if renewal.tzinfo is None:
            renewal = renewal.replace(tzinfo=timezone.utc)
        if renewal > now:
            continue

        catalog = ctx.catalog_for_product(sub.product_id, as_of=now)
        if not catalog or not catalog.list_price or sub.price >= catalog.list_price:
            continue

        monthly, annual = compute_leakage(
            catalog.list_price, sub.price, sub.quantity or 1, sub.billing_interval
        )
        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Renewal passed without price increase",
                severity="medium",
                confidence=CONFIDENCE_MEDIUM,
                customer_id=str(sub.customer_id),
                subscription_id=str(sub.id),
                expected_value=catalog.list_price,
                actual_value=sub.price,
                delta=catalog.list_price - sub.price,
                estimated_monthly_loss=monthly,
                estimated_arr_loss=annual,
                recommendation="Review renewal pricing — expected uplift may not have been applied.",
                evidence=[
                    EvidenceRecord(
                        field="renewal_date",
                        expected=str(catalog.list_price),
                        actual=str(sub.price),
                        reference_ids={"renewal_date": str(renewal.date())},
                    )
                ],
            )
        )

    return findings
