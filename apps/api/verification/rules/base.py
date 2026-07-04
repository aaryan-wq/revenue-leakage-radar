from __future__ import annotations

from decimal import Decimal

from verification.calculator.financial import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW
from verification.types import EvidenceInput, RuleResult, RuleScope, Severity


def make_result(
    *,
    scope: RuleScope,
    expected: Decimal | None,
    actual: Decimal | None,
    difference: Decimal | None,
    calculation,
    severity: Severity = "high",
    confidence: Decimal = CONFIDENCE_HIGH,
    recommendation: str = "",
    evidence: list[EvidenceInput] | None = None,
) -> RuleResult:
    return RuleResult(
        scope=scope,
        expected_value=expected,
        actual_value=actual,
        difference=difference,
        calculation=calculation,
        evidence_fields=evidence or [],
        confidence=confidence,
        severity=severity,
        recommendation=recommendation,
    )


def scope_from_subscription(sub, invoice=None, product_id: str | None = None) -> RuleScope:
    return RuleScope(
        customer_id=str(sub.customer_id),
        subscription_id=str(sub.id),
        invoice_id=str(invoice.id) if invoice else None,
        product_id=product_id or sub.product_id,
    )


def scope_from_line_item(line_item, invoice=None, sub=None) -> RuleScope:
    customer_id = None
    if sub:
        customer_id = str(sub.customer_id)
    elif invoice:
        customer_id = str(invoice.customer_id)
    elif line_item.customer_id:
        customer_id = str(line_item.customer_id)
    return RuleScope(
        customer_id=customer_id,
        subscription_id=str(sub.id) if sub else (str(line_item.subscription_id) if line_item.subscription_id else None),
        invoice_id=str(invoice.id) if invoice else (str(line_item.invoice_id) if line_item.invoice_id else None),
        product_id=line_item.product_id,
    )
