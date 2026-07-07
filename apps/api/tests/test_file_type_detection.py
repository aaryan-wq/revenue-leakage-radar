from unittest.mock import patch

from adapters.generic.adapter import GenericAdapter
from core.enums import FileType
from upload.classification import (
    classify_from_filename,
    classify_from_headers,
    detect_file_type_from_upload,
    resolve_file_type,
)

SUBSCRIPTION_CSV = (
    b"subscription_id,customer_id,status,renewal_date\n"
    b"sub_1,cust_1,active,2025-01-01\n"
)
INVOICE_CSV = (
    b"invoice_id,customer_id,invoice_number,total,currency\n"
    b"inv_1,cust_1,INV-1,100,USD\n"
)
CUSTOMER_CSV = b"customer_id,name\n" b"cust_1,Acme Corp\n"
GARBAGE_CSV = b"foo,bar,baz\n" b"1,2,3\n"


def test_exact_filename_detection():
    result = classify_from_filename("subscriptions.csv")
    assert result is not None
    assert result.file_type == FileType.SUBSCRIPTIONS
    assert result.source == "filename"
    assert result.confidence == 1.0


def test_fuzzy_vendor_export_filename():
    result = classify_from_filename("stripe_subscriptions_export_2024.csv")
    assert result is not None
    assert result.file_type == FileType.SUBSCRIPTIONS
    assert result.source == "filename"
    assert result.confidence >= 0.7


def test_content_detection_from_headers():
    headers = ["subscription_id", "customer_id", "status", "renewal_date"]
    result = classify_from_headers(headers)
    assert result is not None
    assert result.file_type == FileType.SUBSCRIPTIONS
    assert result.source == "content"


def test_unknown_filename_with_subscription_content():
    result = detect_file_type_from_upload("export_jan.csv", SUBSCRIPTION_CSV)
    assert result.file_type == FileType.SUBSCRIPTIONS
    assert result.source in ("content", "combined", "ai")


def test_misnamed_file_prefers_content():
    result = detect_file_type_from_upload("invoices.csv", SUBSCRIPTION_CSV)
    assert result.file_type == FileType.SUBSCRIPTIONS
    assert result.source in ("content", "ai")


def test_combined_agreement():
    result = detect_file_type_from_upload("subscriptions.csv", SUBSCRIPTION_CSV)
    assert result.file_type == FileType.SUBSCRIPTIONS
    assert result.source == "combined"


def test_unrecognizable_file_returns_unknown():
    result = detect_file_type_from_upload("report_q1.csv", GARBAGE_CSV)
    assert result.file_type == FileType.UNKNOWN


def test_ai_tiebreaker_when_signals_disagree():
    weak_subscription_csv = b"subscription_id,customer_id,status\nsub_1,cust_1,active\n"
    with patch("ai.file_type.call_openai_json") as mock_ai:
        mock_ai.return_value = {"file_type": "invoices", "confidence": 0.95}
        result = resolve_file_type(
            "subscriptions.csv",
            ["invoice_id", "customer_id", "invoice_number", "total", "currency"],
            [{"invoice_id": "inv_1", "customer_id": "c1", "invoice_number": "1", "total": "10", "currency": "USD"}],
        )
    assert result.file_type == FileType.INVOICES
    assert result.source == "ai"


def test_ai_skipped_without_api_key():
    from ai.provider import AIProviderError

    with patch("ai.file_type.call_openai_json", side_effect=AIProviderError("no key")):
        result = detect_file_type_from_upload("export_jan.csv", GARBAGE_CSV)
    assert result.file_type == FileType.UNKNOWN


def test_generic_adapter_with_headers():
    adapter = GenericAdapter()
    headers = ["subscription_id", "customer_id", "status"]
    assert adapter.classify_upload("random.csv", headers=headers) == FileType.SUBSCRIPTIONS


def test_generic_adapter_fuzzy_filename():
    adapter = GenericAdapter()
    assert adapter.classify_upload("stripe_invoice_line_items_export.csv") == FileType.INVOICE_LINE_ITEMS


def test_customer_csv_from_content():
    result = detect_file_type_from_upload("data.csv", CUSTOMER_CSV)
    assert result.file_type == FileType.CUSTOMERS
