from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "contract_billing_price_divergence"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    if not ctx.has_crm:
        return []

    findings: list[RuleFinding] = []
    for contract in ctx.crm_contracts:
        if not contract.contract_price or not contract.customer_id:
            continue

        subs = ctx.subscriptions_for_customer(contract.customer_id)
        for sub in subs:
            if not sub.price or sub.price == contract.contract_price:
                continue

            monthly, annual = compute_leakage(
                contract.contract_price, sub.price, sub.quantity or 1, sub.billing_interval
            )
            findings.append(
                RuleFinding(
                    rule_id=RULE_ID,
                    title="Contract vs billing price divergence",
                    severity="high",
                    confidence=CONFIDENCE_HIGH,
                    customer_id=str(sub.customer_id),
                    subscription_id=str(sub.id),
                    expected_value=contract.contract_price,
                    actual_value=sub.price,
                    delta=abs(contract.contract_price - sub.price),
                    estimated_monthly_loss=monthly,
                    estimated_arr_loss=annual,
                    recommendation="Align subscription price with contracted unit price.",
                    evidence=[
                        EvidenceRecord(
                            field="contract_price",
                            expected=str(contract.contract_price),
                            actual=str(sub.price),
                            reference_ids={"contract": contract.external_contract_id},
                        )
                    ],
                )
            )

    return findings
