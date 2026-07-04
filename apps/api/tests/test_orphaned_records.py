"""Tests for orphaned_records rule and unresolved invoice references."""

from __future__ import annotations

import uuid
from decimal import Decimal

from core.enums import DataTier
from models import Invoice, InvoiceLineItem
from verification.context import CanonicalContext
from verification.rules.data_quality.orphaned_records import rule as orphaned_records_rule


def _context_with_orphan_line(*, referenced_invoice_id: str | None = None, invoice_id: uuid.UUID | None = None):
    customer_id = uuid.uuid4()
    invoice = Invoice(
        id=uuid.uuid4(),
        customer_id=customer_id,
        external_invoice_id="inv_1",
        invoice_number="INV-1",
    )
    line_item = InvoiceLineItem(
        id=uuid.uuid4(),
        invoice_id=invoice_id,
        referenced_invoice_id=referenced_invoice_id,
        customer_id=customer_id,
        external_line_item_id="li_orphan",
        product_id="prod_1",
    )
    return CanonicalContext(
        audit_id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        customers=[],
        subscriptions=[],
        invoices=[invoice],
        line_items=[line_item],
        coupons=[],
        price_catalog=[],
        crm_accounts=[],
        crm_contracts=[],
        uploaded_file_types=set(),
        available_entities=set(),
        data_tier=DataTier.TIER_1,
        entity_coverage={},
        has_crm=False,
        has_credit_data=False,
        has_manual_override_data=False,
    )


def test_orphaned_records_fires_on_referenced_invoice_id():
    ctx = _context_with_orphan_line(referenced_invoice_id="inv_missing")
    results = orphaned_records_rule.evaluate(ctx)
    assert len(results) == 1
    assert results[0].calculation.result_monthly == Decimal("0")
    assert results[0].evidence_fields[0].actual == "missing_invoice"


def test_orphaned_records_fires_on_dangling_invoice_uuid():
    missing_invoice_id = uuid.uuid4()
    ctx = _context_with_orphan_line(invoice_id=missing_invoice_id)
    results = orphaned_records_rule.evaluate(ctx)
    assert len(results) == 1


def test_orphaned_records_skips_linked_line_items():
    invoice_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    invoice = Invoice(
        id=invoice_id,
        customer_id=customer_id,
        external_invoice_id="inv_1",
        invoice_number="INV-1",
    )
    line_item = InvoiceLineItem(
        id=uuid.uuid4(),
        invoice_id=invoice_id,
        customer_id=customer_id,
        external_line_item_id="li_ok",
        product_id="prod_1",
    )
    ctx = CanonicalContext(
        audit_id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        customers=[],
        subscriptions=[],
        invoices=[invoice],
        line_items=[line_item],
        coupons=[],
        price_catalog=[],
        crm_accounts=[],
        crm_contracts=[],
        uploaded_file_types=set(),
        available_entities=set(),
        data_tier=DataTier.TIER_1,
        entity_coverage={},
        has_crm=False,
        has_credit_data=False,
        has_manual_override_data=False,
    )
    assert orphaned_records_rule.evaluate(ctx) == []
