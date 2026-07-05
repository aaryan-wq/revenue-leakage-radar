"""Platform adapter registry."""

from storage.reader import read_csv_from_storage, storage_exists

from adapters.base import AdapterOutput
from adapters.generic.adapter import GenericAdapter
from adapters.headers import build_column_mappings
from adapters.stripe.adapter import StripeAdapter
from core.canonical_entities import entities_from_uploaded_files
from core.enums import FileType, Platform
from models import Upload

_GENERIC = GenericAdapter()
_STRIPE = StripeAdapter()

PLATFORM_HEADER_HINTS: dict[str, list[str]] = {
    "stripe": ["stripe_customer_id", "subscription_item", "amount_due"],
    "chargebee": ["subscription_id", "customer_id", "plan_id"],
    "maxio": ["subscription_id", "customer_id"],
    "zuora": ["subscriptionnumber", "accountnumber"],
}


def detect_platform_from_headers(file_headers: dict[FileType, list[str]]) -> Platform:
    all_headers: set[str] = set()
    for headers in file_headers.values():
        all_headers.update(h.lower() for h in headers)

    for platform, hints in PLATFORM_HEADER_HINTS.items():
        if any(hint in all_headers for hint in hints):
            try:
                return Platform(platform)
            except ValueError:
                continue
    return Platform.GENERIC


def get_adapter(platform: Platform) -> GenericAdapter:
    if platform == Platform.STRIPE:
        return _STRIPE
    return _GENERIC


def read_upload_headers(uploads: list[Upload]) -> dict[FileType, list[str]]:
    file_headers: dict[FileType, list[str]] = {}
    for upload in uploads:
        file_type = FileType(upload.file_type)
        if file_type == FileType.UNKNOWN:
            continue
        if not storage_exists(upload.storage_path):
            continue
        df = read_csv_from_storage(upload.storage_path, n_rows=0, infer_schema_length=0)
        file_headers[file_type] = df.columns
    return file_headers


def run_adapter_mapping(uploads: list[Upload]) -> tuple[Platform, dict[str, dict[str, str]], set[FileType]]:
    file_headers = read_upload_headers(uploads)
    if not file_headers:
        return Platform.GENERIC, {}, set()

    platform = detect_platform_from_headers(file_headers)
    adapter = get_adapter(platform)
    mappings = adapter.map_columns(file_headers)
    if not mappings:
        mappings = build_column_mappings(file_headers)
    uploaded_types = set(file_headers.keys())
    return platform, mappings, uploaded_types


def build_adapter_output(
    platform: Platform,
    mappings: dict[str, dict[str, str]],
    uploaded_types: set[FileType],
) -> AdapterOutput:
    return AdapterOutput(
        platform=platform,
        column_mappings=mappings,
        detected_entities=entities_from_uploaded_files(uploaded_types),
    )
