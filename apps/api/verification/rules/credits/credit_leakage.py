from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_MEDIUM
from verification.calculator.trace import TraceBuilder
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result
from verification.types import EvidenceInput, RuleResult, RuleScope


def _has_credit_data(ctx: CanonicalContext) -> tuple[bool, str | None]:
    if not ctx.has_credit_data:
        return False, "Credit amount data not present in invoices"
    return True, None


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="credit_leakage",
        name="Credit Leakage",
        category="credits",
        purpose="Detect credit amounts that exceed invoice subtotal without proper adjustment.",
        trigger_description="invoice.credit_amount > invoice.subtotal",
        ignored_cases="Zero credits; proportional credits.",
        severity_default="medium",
        leak_family="operational",
        recommendation_template="Reconcile credit memo with invoice adjustments.",
        eligibility_conditions=_has_credit_data,
    )
    spec.field(CanonicalEntity.INVOICE, "credit_amount")
    return spec


class CreditLeakageRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for invoice in ctx.invoices:
            if not invoice.credit_amount or invoice.credit_amount <= 0:
                continue
            subtotal = invoice.subtotal or Decimal("0")
            if subtotal > 0 and invoice.credit_amount <= subtotal:
                continue
            leak_amount = invoice.credit_amount if subtotal <= 0 else invoice.credit_amount - subtotal
            recoverable = leak_amount.quantize(Decimal("0.0001"))
            refs = {"invoice": invoice.external_invoice_id or str(invoice.id)}
            trace = (
                TraceBuilder(semantics="one_time")
                .add("credit_amount", "Credit amount", invoice.credit_amount, source_refs=refs)
                .add("invoice_subtotal", "Invoice subtotal", subtotal, source_refs=refs)
                .add("recoverable_amount", "Recoverable amount", recoverable, source_refs=refs)
                .finish(recoverable, Decimal("0"))
            )
            findings.append(
                make_result(
                    scope=RuleScope(
                        customer_id=str(invoice.customer_id),
                        subscription_id=str(invoice.subscription_id) if invoice.subscription_id else None,
                        invoice_id=str(invoice.id),
                    ),
                    expected=Decimal("0"),
                    actual=leak_amount,
                    difference=leak_amount,
                    calculation=trace,
                    severity="medium",
                    confidence=CONFIDENCE_MEDIUM,
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="credit_amount",
                            expected="<= subtotal",
                            actual=str(invoice.credit_amount),
                            reference_ids={"invoice": invoice.external_invoice_id or str(invoice.id)},
                        )
                    ],
                )
            )
        return findings


rule = CreditLeakageRule()
