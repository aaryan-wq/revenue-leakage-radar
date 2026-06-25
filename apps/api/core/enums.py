import enum


class AuditStatus(str, enum.Enum):
    CREATED = "created"
    UPLOADING = "uploading"
    MAPPING = "mapping"
    VALIDATING = "validating"
    NORMALIZING = "normalizing"
    READY_FOR_SCAN = "ready_for_scan"
    SCANNING = "scanning"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    UPLOAD_FAILED = "upload_failed"
    VALIDATION_FAILED = "validation_failed"
    PROCESSING_FAILED = "processing_failed"
    PAYMENT_PENDING = "payment_pending"


class UploadStatus(str, enum.Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    FAILED = "failed"


class FileType(str, enum.Enum):
    SUBSCRIPTIONS = "subscriptions"
    INVOICES = "invoices"
    INVOICE_LINE_ITEMS = "invoice_line_items"
    COUPONS = "coupons"
    PRICE_CATALOG = "price_catalog"
    CRM_ACCOUNTS = "crm_accounts"
    CRM_OPPORTUNITIES = "crm_opportunities"
    CRM_CONTRACTS = "crm_contracts"
    UNKNOWN = "unknown"


FILENAME_TO_FILE_TYPE: dict[str, FileType] = {
    "subscriptions": FileType.SUBSCRIPTIONS,
    "subscriptions.csv": FileType.SUBSCRIPTIONS,
    "invoices": FileType.INVOICES,
    "invoices.csv": FileType.INVOICES,
    "invoice_line_items": FileType.INVOICE_LINE_ITEMS,
    "invoice_line_items.csv": FileType.INVOICE_LINE_ITEMS,
    "coupons": FileType.COUPONS,
    "coupons.csv": FileType.COUPONS,
    "price_catalog": FileType.PRICE_CATALOG,
    "price_catalog.csv": FileType.PRICE_CATALOG,
    "accounts": FileType.CRM_ACCOUNTS,
    "accounts.csv": FileType.CRM_ACCOUNTS,
    "opportunities": FileType.CRM_OPPORTUNITIES,
    "opportunities.csv": FileType.CRM_OPPORTUNITIES,
    "contracts": FileType.CRM_CONTRACTS,
    "contracts.csv": FileType.CRM_CONTRACTS,
}

class Platform(str, enum.Enum):
    STRIPE = "stripe"
    CHARGEBEE = "chargebee"
    MAXIO = "maxio"
    ZUORA = "zuora"
    GENERIC = "generic"


class ValidationResult(str, enum.Enum):
    READY = "ready"
    WARNINGS = "warnings"
    BLOCKING = "blocking"


PROCESSING_STATUSES: set[AuditStatus] = {
    AuditStatus.MAPPING,
    AuditStatus.VALIDATING,
    AuditStatus.NORMALIZING,
}


SCAN_PROCESSING_STATUSES: set[AuditStatus] = {
    AuditStatus.SCANNING,
    AuditStatus.GENERATING_REPORT,
}


REQUIRED_BILLING_FILE_TYPES: set[FileType] = {
    FileType.SUBSCRIPTIONS,
    FileType.INVOICES,
    FileType.INVOICE_LINE_ITEMS,
    FileType.COUPONS,
    FileType.PRICE_CATALOG,
}
