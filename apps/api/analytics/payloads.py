"""Build common analytics payloads from audit and related models."""

from __future__ import annotations

import uuid
from typing import Any

from core.canonical_entities import CanonicalEntity
from core.enums import FileType
from models import Audit

BILLING_FILE_TYPES = frozenset(
    {
        FileType.CUSTOMERS,
        FileType.SUBSCRIPTIONS,
        FileType.INVOICES,
        FileType.INVOICE_LINE_ITEMS,
        FileType.COUPONS,
        FileType.PRICE_CATALOG,
    }
)

CRM_FILE_TYPES = frozenset(
    {
        FileType.CRM_ACCOUNTS,
        FileType.CRM_OPPORTUNITIES,
        FileType.CRM_CONTRACTS,
    }
)


def audit_distinct_id(audit: Audit) -> str:
    if audit.clerk_user_id:
        return audit.clerk_user_id
    return f"audit_session:{audit.session_token}"


def count_upload_files(audit: Audit) -> tuple[int, int, int]:
    uploaded = [
        upload
        for upload in audit.uploads
        if upload.status in ("uploaded", "purged")
    ]
    billing = sum(1 for upload in uploaded if upload.file_type in {ft.value for ft in BILLING_FILE_TYPES})
    crm = sum(1 for upload in uploaded if upload.file_type in {ft.value for ft in CRM_FILE_TYPES})
    return len(uploaded), billing, crm


def compute_data_presence(available_entities: set[CanonicalEntity] | list[str] | None) -> dict[str, bool]:
    if not available_entities:
        entities: set[CanonicalEntity] = set()
    elif isinstance(available_entities, list):
        entities = {CanonicalEntity(entity) for entity in available_entities if entity in CanonicalEntity._value2member_map_}
    else:
        entities = set(available_entities)

    billing_present = bool(
        entities
        & {
            CanonicalEntity.CUSTOMER,
            CanonicalEntity.SUBSCRIPTION,
            CanonicalEntity.INVOICE,
            CanonicalEntity.INVOICE_LINE_ITEM,
            CanonicalEntity.PRICE,
            CanonicalEntity.COUPON,
        }
    )
    crm_present = bool(
        entities
        & {
            CanonicalEntity.ACCOUNT,
            CanonicalEntity.OPPORTUNITY,
            CanonicalEntity.CONTRACT,
        }
    )

    return {
        "billing_data_present": billing_present,
        "crm_data_present": crm_present,
        "invoice_data_present": CanonicalEntity.INVOICE in entities,
        "subscription_data_present": CanonicalEntity.SUBSCRIPTION in entities,
        "line_item_data_present": CanonicalEntity.INVOICE_LINE_ITEM in entities,
        "price_data_present": CanonicalEntity.PRICE in entities,
        "coupon_data_present": CanonicalEntity.COUPON in entities,
        "credit_data_present": CanonicalEntity.INVOICE in entities,
    }


def infer_crm_platform(audit: Audit) -> str | None:
    if not audit.crm_data_present:
        return None
    return audit.crm_platform_detected or "generic"


def audit_lifecycle_properties(audit: Audit) -> dict[str, Any]:
    csv_count, billing_count, crm_count = count_upload_files(audit)
    return {
        "audit_id": str(audit.id),
        "session_id": audit.session_token,
        "user_id": audit.clerk_user_id,
        "is_anonymous": audit.is_anonymous,
        "audit_type": audit.audit_type,
        "billing_platform_detected": audit.billing_platform_detected or audit.platform,
        "crm_platform_detected": infer_crm_platform(audit),
        "csv_file_count": csv_count or audit.csv_file_count,
        "billing_file_count": billing_count or audit.billing_file_count,
        "crm_file_count": crm_count or audit.crm_file_count,
        "billing_data_present": audit.billing_data_present,
        "crm_data_present": audit.crm_data_present,
    }


def verification_summary_properties(audit: Audit) -> dict[str, Any]:
    base = audit_lifecycle_properties(audit)
    base.update(
        {
            "verification_duration_ms": audit.verification_duration_ms,
            "rules_total": audit.rules_total,
            "rules_executed": audit.rules_executed,
            "rules_skipped": audit.rules_skipped,
            "rules_failed": audit.rules_failed,
            "findings_total": audit.findings_total,
            "estimated_monthly_leakage": float(audit.estimated_monthly_leakage)
            if audit.estimated_monthly_leakage is not None
            else None,
            "estimated_annual_leakage": float(audit.estimated_annual_leakage)
            if audit.estimated_annual_leakage is not None
            else None,
            "coverage_score": float(audit.coverage_score) if audit.coverage_score is not None else None,
            "confidence_score": float(audit.confidence_score) if audit.confidence_score is not None else None,
            "top_rule_category": audit.top_rule_category,
        }
    )
    return base


def upload_file_properties(
    audit: Audit,
    *,
    file_id: uuid.UUID | str,
    original_filename: str,
    detected_file_type: str,
    file_size_bytes: int,
    row_count: int | None = None,
    column_count: int | None = None,
    validation_status: str | None = None,
    missing_required_fields_count: int | None = None,
    unknown_columns_count: int | None = None,
    source_platform_guess: str | None = None,
    replaced: bool = False,
    detection_source: str | None = None,
) -> dict[str, Any]:
    props = audit_lifecycle_properties(audit)
    props.update(
        {
            "file_id": str(file_id),
            "original_filename": original_filename,
            "detected_file_type": detected_file_type,
            "detection_source": detection_source,
            "source_platform_guess": source_platform_guess or audit.platform,
            "row_count": row_count,
            "column_count": column_count,
            "file_size_bytes": file_size_bytes,
            "validation_status": validation_status,
            "missing_required_fields_count": missing_required_fields_count,
            "unknown_columns_count": unknown_columns_count,
            "replaced": replaced,
        }
    )
    return props
