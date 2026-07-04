from adapters.generic.adapter import GenericAdapter
from adapters.registry import detect_platform_from_headers
from adapters.stripe.adapter import StripeAdapter
from core.enums import FileType, Platform


def test_generic_adapter_classifies_filename():
    adapter = GenericAdapter()
    assert adapter.classify_upload("invoice_line_items.csv") == FileType.INVOICE_LINE_ITEMS
    assert adapter.classify_upload("accounts.csv") == FileType.CRM_ACCOUNTS
    assert adapter.classify_upload("crm_accounts.csv") == FileType.CRM_ACCOUNTS
    assert adapter.classify_upload("contracts.csv") == FileType.CRM_CONTRACTS
    assert adapter.classify_upload("crm_contracts.csv") == FileType.CRM_CONTRACTS
    assert adapter.classify_upload("unknown.csv") == FileType.UNKNOWN


def test_stripe_platform_detection():
    headers = {
        FileType.SUBSCRIPTIONS: ["stripe_customer_id", "subscription_item", "status"],
    }
    assert detect_platform_from_headers(headers) == Platform.STRIPE


def test_stripe_adapter_inherits_mapping():
    adapter = StripeAdapter()
    headers = {
        FileType.INVOICES: ["Invoice ID", "Customer ID", "Invoice Number", "Total", "Currency"],
    }
    mappings = adapter.map_columns(headers)
    assert "invoice_id" in mappings.get(FileType.INVOICES.value, {}).values()
