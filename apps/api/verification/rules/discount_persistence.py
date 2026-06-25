from datetime import datetime, timezone

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "discount_past_contract_end"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    now = datetime.now(timezone.utc)

    if not ctx.has_crm:
        return findings

    for sub in ctx.subscriptions:
        if not sub.coupon_id:
            continue
        coupon = ctx.coupon_by_code(sub.coupon_id)
        if not coupon or not coupon.active:
            continue

        contracts = ctx.contracts_for_customer(sub.customer_id)
        for contract in contracts:
            if not contract.end_date:
                continue
            end = contract.end_date
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            if end >= now:
                continue

            findings.append(
                RuleFinding(
                    rule_id=RULE_ID,
                    title="Discount active beyond contract end",
                    severity="high",
                    confidence=CONFIDENCE_HIGH,
                    customer_id=str(sub.customer_id),
                    subscription_id=str(sub.id),
                    recommendation="Remove discount — contract terms have expired.",
                    evidence=[
                        EvidenceRecord(
                            field="contract_end_date",
                            expected=str(end.date()),
                            actual=f"coupon={coupon.code} still active",
                            reference_ids={"contract": contract.external_contract_id},
                        )
                    ],
                )
            )

    return findings
