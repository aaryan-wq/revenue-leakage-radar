from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result
from verification.types import EvidenceInput, RuleResult, RuleScope


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="orphaned_records",
        name="Orphaned Records",
        category="data_quality",
        purpose="Detect line items or invoices referencing missing parent records.",
        trigger_description="line_item without resolved invoice parent",
        ignored_cases="Fully linked records.",
        severity_default="low",
        leak_family="operational",
        recommendation_template="Link orphaned records to parent entities.",
    )
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "line_item_id")
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "product_id")
    return spec


class OrphanedRecordsRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        invoice_ids = {invoice.id for invoice in ctx.invoices}

        for line_item in ctx.line_items:
            orphaned = False
            reason = ""
            if line_item.referenced_invoice_id:
                orphaned = True
                reason = "missing_invoice"
            elif line_item.invoice_id is not None and line_item.invoice_id not in invoice_ids:
                orphaned = True
                reason = "missing_invoice"
            if not orphaned:
                continue
            trace = FinancialCalculator.compute_zero_leakage(semantics="operational")
            ref_ids: dict[str, str] = {
                "line_item_id": line_item.external_line_item_id or str(line_item.id),
            }
            if line_item.referenced_invoice_id:
                ref_ids["referenced_invoice_id"] = line_item.referenced_invoice_id
            findings.append(
                make_result(
                    scope=RuleScope(
                        customer_id=str(line_item.customer_id) if line_item.customer_id else None,
                        subscription_id=str(line_item.subscription_id) if line_item.subscription_id else None,
                        invoice_id=str(line_item.invoice_id) if line_item.invoice_id else None,
                        product_id=line_item.product_id,
                    ),
                    expected=Decimal("0"),
                    actual=Decimal("0"),
                    difference=Decimal("0"),
                    calculation=trace,
                    severity="low",
                    confidence=Decimal("90"),
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="orphan_type",
                            expected="linked",
                            actual=reason,
                            reference_ids=ref_ids,
                        )
                    ],
                )
            )
        return findings


rule = OrphanedRecordsRule()
