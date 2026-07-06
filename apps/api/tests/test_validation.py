import polars as pl

from ai.fallback import build_fallback_mappings, map_header_to_canonical
from core.data_tiers import (
    get_audit_data_tier,
    missing_recommended_files,
    missing_tier_0_files,
    tier_0_complete,
)
from core.enums import DataTier, FileType
from validation.duplicates import validate_duplicates
from validation.schema import validate_schema
from validation.service import run_validation
from ingestion.types import ValidationReport


def test_map_header_synonym():
    assert map_header_to_canonical("Customer ID", FileType.SUBSCRIPTIONS) == "customer_id"
    assert map_header_to_canonical("subscription_id", FileType.SUBSCRIPTIONS) == "subscription_id"
    assert map_header_to_canonical("customerId", FileType.SUBSCRIPTIONS) == "customer_id"
    assert map_header_to_canonical("StartDate", FileType.SUBSCRIPTIONS) == "start_date"


def test_fallback_platform_detection():
    headers = {
        FileType.SUBSCRIPTIONS: ["subscription_id", "customer_id", "status"],
        FileType.INVOICES: ["invoice_id", "customer_id", "invoice_number", "total", "currency"],
    }
    platform, mappings = build_fallback_mappings(headers)
    assert platform in ("generic", "chargebee", "stripe")
    assert "subscription_id" in mappings.get(FileType.SUBSCRIPTIONS.value, {}).values()


def test_schema_validation_missing_column():
    frames = {
        FileType.SUBSCRIPTIONS: pl.DataFrame({"subscription_id": ["sub_1"], "customer_id": ["c1"]}),
    }
    report = ValidationReport()
    validate_schema(frames, report, uploaded={FileType.SUBSCRIPTIONS})
    assert report.has_blocking
    assert any(i.code == "missing_column" for i in report.issues)


def test_tier_0_only_passes_without_tier_1_files():
    frames = {
        FileType.INVOICE_LINE_ITEMS: pl.DataFrame(
            {
                "line_item_id": ["li_1"],
                "product_id": ["prod_1"],
                "quantity": [1],
                "unit_price": [100.0],
            }
        ),
    }
    uploaded = {FileType.INVOICE_LINE_ITEMS}
    report = run_validation(frames, uploaded)
    assert not report.has_blocking
    assert report.summary["data_tier"] == DataTier.TIER_0.value
    assert FileType.PRICE_CATALOG.value in report.summary["recommended_missing"]


def test_tier_0_complete_with_any_billing_file():
    uploaded = {FileType.SUBSCRIPTIONS}
    assert tier_0_complete(uploaded)
    assert FileType.INVOICE_LINE_ITEMS in missing_tier_0_files(uploaded)


def test_duplicate_primary_key_detection():
    frames = {
        FileType.SUBSCRIPTIONS: pl.DataFrame(
            {
                "subscription_id": ["sub_1", "sub_1"],
                "customer_id": ["c1", "c2"],
                "status": ["active", "active"],
            }
        ),
    }
    report = ValidationReport()
    validate_duplicates(frames, report)
    assert report.has_blocking


def test_price_catalog_allows_multiple_versions_per_product():
    frames = {
        FileType.PRICE_CATALOG: pl.DataFrame(
            {
                "product_id": ["prod_starter_mo", "prod_starter_mo"],
                "version": ["v1", "v2"],
                "effective_date": ["2023-01-01", "2024-07-01"],
                "list_price": [49.0, 56.35],
                "currency": ["USD", "USD"],
            }
        ),
    }
    report = ValidationReport()
    validate_duplicates(frames, report)
    assert not report.has_blocking


def test_orphan_line_item_invoice_is_warning_not_blocking():
    frames = {
        FileType.CUSTOMERS: pl.DataFrame({"customer_id": ["c1"], "name": ["Acme"]}),
        FileType.INVOICES: pl.DataFrame(
            {
                "invoice_id": ["inv_1"],
                "customer_id": ["c1"],
                "invoice_number": ["INV-1"],
                "total": [100.0],
                "currency": ["USD"],
            }
        ),
        FileType.INVOICE_LINE_ITEMS: pl.DataFrame(
            {
                "line_item_id": ["li_orphan"],
                "invoice_id": ["inv_missing"],
                "customer_id": ["c1"],
                "product_id": ["prod_1"],
                "quantity": [1],
                "unit_price": [99.0],
            }
        ),
    }
    uploaded = {FileType.CUSTOMERS, FileType.INVOICES, FileType.INVOICE_LINE_ITEMS}
    report = run_validation(frames, uploaded)
    assert not report.has_blocking
    assert any(i.code == "orphan_line_item_invoice" and i.severity == "warning" for i in report.issues)
