import polars as pl

from ai.fallback import build_fallback_mappings, map_header_to_canonical
from core.enums import FileType
from validation.duplicates import validate_duplicates
from validation.schema import validate_schema
from ingestion.types import ValidationReport


def test_map_header_synonym():
    assert map_header_to_canonical("Customer ID", FileType.SUBSCRIPTIONS) == "customer_id"
    assert map_header_to_canonical("subscription_id", FileType.SUBSCRIPTIONS) == "subscription_id"


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
    validate_schema(frames, report)
    assert report.has_blocking
    assert any(i.code == "missing_column" for i in report.issues)


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
