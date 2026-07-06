"""Integration tests for batch canonical transformer DB writes."""

from __future__ import annotations

import secrets
import uuid
from pathlib import Path

import polars as pl
import pytest

from canonical.transformer import clear_canonical_data, run_canonical_transform
from core.enums import AuditStatus, FileType
from database.session import SessionLocal
from ingestion.types import IngestionContext
from models import Audit, Company, CrmAccount, CrmContract, Customer, Invoice, InvoiceLineItem, Subscription

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ACMECRM = Path(__file__).resolve().parents[3] / "testdata" / "acmecrm"


def _load_fixture(name: str) -> pl.DataFrame:
    return pl.read_csv(FIXTURES / name)


def _tier0_context() -> IngestionContext:
    return IngestionContext(
        audit_id=str(uuid.uuid4()),
        frames={
            FileType.INVOICE_LINE_ITEMS: _load_fixture("invoice_line_items.csv"),
            FileType.PRICE_CATALOG: _load_fixture("price_catalog.csv"),
        },
        uploaded_file_types={FileType.INVOICE_LINE_ITEMS, FileType.PRICE_CATALOG},
    )


def _full_context() -> IngestionContext:
    frames = {
        FileType.CUSTOMERS: pl.read_csv(ACMECRM / "customers.csv"),
        FileType.SUBSCRIPTIONS: pl.read_csv(ACMECRM / "subscriptions.csv"),
        FileType.INVOICES: pl.read_csv(ACMECRM / "invoices.csv"),
        FileType.INVOICE_LINE_ITEMS: pl.read_csv(ACMECRM / "invoice_line_items.csv"),
        FileType.PRICE_CATALOG: pl.read_csv(ACMECRM / "price_catalog.csv"),
        FileType.COUPONS: pl.read_csv(ACMECRM / "coupons.csv"),
    }
    return IngestionContext(
        audit_id=str(uuid.uuid4()),
        frames=frames,
        uploaded_file_types=set(frames.keys()),
    )


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


def _create_audit(db) -> Audit:
    audit = Audit(
        session_token=secrets.token_urlsafe(32),
        status=AuditStatus.READY_FOR_SCAN.value,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def _cleanup_audit(db, audit: Audit) -> None:
    if audit.company_id:
        clear_canonical_data(db, audit.company_id)
    db.delete(audit)
    if audit.company_id:
        company = db.query(Company).filter(Company.id == audit.company_id).first()
        if company:
            db.delete(company)
    db.commit()


def test_tier0_transform_creates_stub_invoices_and_line_items(db_session):
    audit = _create_audit(db_session)
    try:
        result = run_canonical_transform(db_session, audit, _tier0_context())

        assert result.counts["customers"] >= 1
        assert result.counts["stub_invoices"] >= 1
        assert result.counts["invoice_line_items"] == 2
        assert result.counts["price_catalog"] >= 1

        company_id = audit.company_id
        assert company_id is not None

        customers = db_session.query(Customer).filter(Customer.company_id == company_id).all()
        invoices = db_session.query(Invoice).filter(Invoice.customer_id.in_([c.id for c in customers])).all()
        line_items = db_session.query(InvoiceLineItem).filter(
            InvoiceLineItem.invoice_id.in_([i.id for i in invoices])
        ).all()

        assert len(customers) >= 1
        assert len(invoices) >= 2
        assert len(line_items) == 2
        for line_item in line_items:
            assert line_item.invoice_id is not None
    finally:
        _cleanup_audit(db_session, audit)


def test_full_dataset_transform_fk_integrity(db_session):
    if not ACMECRM.exists():
        pytest.skip("AcmeCRM testdata not available")

    audit = _create_audit(db_session)
    try:
        result = run_canonical_transform(db_session, audit, _full_context())

        assert result.counts["customers"] > 0
        assert result.counts["subscriptions"] > 0
        assert result.counts["invoices"] > 0
        assert result.counts["invoice_line_items"] > 0

        company_id = audit.company_id
        customers = db_session.query(Customer).filter(Customer.company_id == company_id).all()
        customer_ids = {customer.id for customer in customers}

        subscriptions = db_session.query(Subscription).filter(
            Subscription.customer_id.in_(customer_ids)
        ).all()
        for subscription in subscriptions:
            assert subscription.customer_id in customer_ids

        invoices = db_session.query(Invoice).filter(Invoice.customer_id.in_(customer_ids)).all()
        for invoice in invoices:
            assert invoice.customer_id in customer_ids
            if invoice.subscription_id:
                sub_ids = {subscription.id for subscription in subscriptions}
                assert invoice.subscription_id in sub_ids
    finally:
        _cleanup_audit(db_session, audit)


def test_retransform_replaces_canonical_data(db_session):
    audit = _create_audit(db_session)
    try:
        ctx = _tier0_context()
        first = run_canonical_transform(db_session, audit, ctx)
        second = run_canonical_transform(db_session, audit, ctx)

        assert first.counts["invoice_line_items"] == second.counts["invoice_line_items"]
        company_id = audit.company_id
        customer_ids = [
            customer.id
            for customer in db_session.query(Customer).filter(Customer.company_id == company_id).all()
        ]
        invoice_ids = [
            invoice.id
            for invoice in db_session.query(Invoice).filter(Invoice.customer_id.in_(customer_ids)).all()
        ]
        line_item_count = db_session.query(InvoiceLineItem).filter(
            InvoiceLineItem.invoice_id.in_(invoice_ids)
        ).count()
        assert line_item_count == second.counts["invoice_line_items"]
    finally:
        _cleanup_audit(db_session, audit)


def test_missing_subscription_fields_records_row_error(db_session):
    audit = _create_audit(db_session)
    try:
        ctx = IngestionContext(
            audit_id=str(audit.id),
            frames={
                FileType.SUBSCRIPTIONS: pl.DataFrame(
                    {
                        "subscription_id": [""],
                        "customer_id": [""],
                        "product_id": ["prod_x"],
                        "price": ["10.00"],
                    }
                ),
            },
            uploaded_file_types={FileType.SUBSCRIPTIONS},
        )
        result = run_canonical_transform(db_session, audit, ctx)

        assert result.counts.get("subscriptions", 0) == 0
        assert any("Missing subscription_id" in error.message for error in result.row_errors)
    finally:
        _cleanup_audit(db_session, audit)
