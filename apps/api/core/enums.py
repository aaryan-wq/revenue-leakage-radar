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
    PURGED = "purged"


class DataTier(str, enum.Enum):
    INSUFFICIENT = "insufficient"
    TIER_0 = "tier_0"
    TIER_1 = "tier_1"
    TIER_2_PLUS = "tier_2_plus"


class FileType(str, enum.Enum):
    CUSTOMERS = "customers"
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
    "customers": FileType.CUSTOMERS,
    "customers.csv": FileType.CUSTOMERS,
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
    "prices": FileType.PRICE_CATALOG,
    "prices.csv": FileType.PRICE_CATALOG,
    "accounts": FileType.CRM_ACCOUNTS,
    "accounts.csv": FileType.CRM_ACCOUNTS,
    "crm_accounts": FileType.CRM_ACCOUNTS,
    "crm_accounts.csv": FileType.CRM_ACCOUNTS,
    "opportunities": FileType.CRM_OPPORTUNITIES,
    "opportunities.csv": FileType.CRM_OPPORTUNITIES,
    "crm_opportunities": FileType.CRM_OPPORTUNITIES,
    "crm_opportunities.csv": FileType.CRM_OPPORTUNITIES,
    "contracts": FileType.CRM_CONTRACTS,
    "contracts.csv": FileType.CRM_CONTRACTS,
    "crm_contracts": FileType.CRM_CONTRACTS,
    "crm_contracts.csv": FileType.CRM_CONTRACTS,
}

# Fuzzy filename tokens, longest/most-specific first for substring matching.
FILENAME_ALIASES: list[tuple[str, FileType, float]] = [
    ("invoice_line_items", FileType.INVOICE_LINE_ITEMS, 0.8),
    ("invoice_line_item", FileType.INVOICE_LINE_ITEMS, 0.8),
    ("line_items", FileType.INVOICE_LINE_ITEMS, 0.75),
    ("lineitems", FileType.INVOICE_LINE_ITEMS, 0.75),
    ("price_catalog", FileType.PRICE_CATALOG, 0.8),
    ("pricecatalog", FileType.PRICE_CATALOG, 0.75),
    ("crm_opportunities", FileType.CRM_OPPORTUNITIES, 0.8),
    ("crm_opportunity", FileType.CRM_OPPORTUNITIES, 0.8),
    ("crm_accounts", FileType.CRM_ACCOUNTS, 0.8),
    ("crm_account", FileType.CRM_ACCOUNTS, 0.8),
    ("crm_contracts", FileType.CRM_CONTRACTS, 0.8),
    ("crm_contract", FileType.CRM_CONTRACTS, 0.8),
    ("subscriptions", FileType.SUBSCRIPTIONS, 0.8),
    ("subscription", FileType.SUBSCRIPTIONS, 0.75),
    ("customers", FileType.CUSTOMERS, 0.8),
    ("customer", FileType.CUSTOMERS, 0.7),
    ("invoices", FileType.INVOICES, 0.8),
    ("invoice", FileType.INVOICES, 0.7),
    ("opportunities", FileType.CRM_OPPORTUNITIES, 0.75),
    ("opportunity", FileType.CRM_OPPORTUNITIES, 0.7),
    ("contracts", FileType.CRM_CONTRACTS, 0.75),
    ("contract", FileType.CRM_CONTRACTS, 0.7),
    ("accounts", FileType.CRM_ACCOUNTS, 0.7),
    ("account", FileType.CRM_ACCOUNTS, 0.65),
    ("coupons", FileType.COUPONS, 0.8),
    ("coupon", FileType.COUPONS, 0.75),
    ("prices", FileType.PRICE_CATALOG, 0.7),
    ("catalog", FileType.PRICE_CATALOG, 0.65),
]


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


class CheckoutPlan(str, enum.Enum):
    SINGLE_REPORT = "single_report"
    ANNUAL_MEMBERSHIP = "annual_membership"


class MembershipPlan(str, enum.Enum):
    NONE = "none"
    ANNUAL = "annual"


class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"


class PurchasePlan(str, enum.Enum):
    SINGLE_REPORT = "single_report"
    MEMBERSHIP_CREDIT = "membership_credit"
    ANNUAL_MEMBERSHIP = "annual_membership"


# No hard-required file types, any billing export satisfies the minimum upload.
REQUIRED_BILLING_FILE_TYPES: set[FileType] = set()
