from __future__ import annotations

from collections import defaultdict
from datetime import timedelta, timezone
from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_MEDIUM, FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result
from verification.types import EvidenceInput, RuleResult, RuleScope

DISCOUNT_ABUSE_THRESHOLD = 3
ROLLING_MONTHS = 12


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="excessive_discount",
        name="Excessive Discount",
        category="discounts",
        purpose="Detect customers receiving discounts too frequently in a rolling period.",
        trigger_description=f"customer receives discount >= {DISCOUNT_ABUSE_THRESHOLD} times in rolling 12 months",
        ignored_cases="Infrequent discount usage.",
        severity_default="medium",
        leak_family="discount_integrity",
        recommendation_template="Review discount approval policy for this customer.",
    )
    spec.field(CanonicalEntity.INVOICE, "discount")
    spec.field(CanonicalEntity.INVOICE, "customer_id")
    spec.field(CanonicalEntity.INVOICE, "invoice_date")
    return spec


class ExcessiveDiscountRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        ref = ctx.reference_date
        cutoff = ref - timedelta(days=ROLLING_MONTHS * 30)

        by_customer: dict[str, list] = defaultdict(list)
        for invoice in ctx.invoices:
            if not invoice.discount or invoice.discount <= 0 or not invoice.customer_id or not invoice.invoice_date:
                continue
            invoice_date = invoice.invoice_date
            if invoice_date.tzinfo is None:
                invoice_date = invoice_date.replace(tzinfo=timezone.utc)
            if invoice_date < cutoff:
                continue
            by_customer[str(invoice.customer_id)].append(invoice)

        for customer_id, invoices in by_customer.items():
            if len(invoices) < DISCOUNT_ABUSE_THRESHOLD:
                continue
            total_discount = sum((inv.discount or Decimal("0") for inv in invoices), Decimal("0"))
            monthly, annual, trace = FinancialCalculator.compute_period_leakage(
                total_discount / Decimal(str(ROLLING_MONTHS)),
                Decimal("0"),
                "monthly",
            )
            findings.append(
                make_result(
                    scope=RuleScope(
                        customer_id=customer_id,
                        invoice_id=str(invoices[0].id),
                    ),
                    expected=Decimal(str(DISCOUNT_ABUSE_THRESHOLD)),
                    actual=Decimal(str(len(invoices))),
                    difference=Decimal(str(len(invoices) - DISCOUNT_ABUSE_THRESHOLD)),
                    calculation=trace,
                    confidence=CONFIDENCE_MEDIUM,
                    severity="medium",
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="discount_frequency",
                            expected=f"<={DISCOUNT_ABUSE_THRESHOLD} in {ROLLING_MONTHS}mo",
                            actual=str(len(invoices)),
                            reference_ids={"customer_id": customer_id},
                        )
                    ],
                )
            )
        return findings


rule = ExcessiveDiscountRule()
