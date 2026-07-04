"""Canonical Entity Model (CEM), verification and tier framework."""

import enum

from core.enums import FileType


class CanonicalEntity(str, enum.Enum):
    CUSTOMER = "customer"
    SUBSCRIPTION = "subscription"
    INVOICE = "invoice"
    INVOICE_LINE_ITEM = "invoice_line_item"
    PRICE = "price"
    COUPON = "coupon"
    CONTRACT = "contract"
    ACCOUNT = "account"
    OPPORTUNITY = "opportunity"


# Any billing entity satisfies the minimum upload requirement.
MINIMUM_BILLING_ENTITIES: frozenset[CanonicalEntity] = frozenset(
    {
        CanonicalEntity.CUSTOMER,
        CanonicalEntity.SUBSCRIPTION,
        CanonicalEntity.INVOICE,
        CanonicalEntity.INVOICE_LINE_ITEM,
        CanonicalEntity.PRICE,
        CanonicalEntity.COUPON,
    }
)

TIER_0_REQUIRED_ENTITIES: frozenset[CanonicalEntity] = MINIMUM_BILLING_ENTITIES

TIER_1_RECOMMENDED_ENTITIES: frozenset[CanonicalEntity] = frozenset(
    {
        CanonicalEntity.SUBSCRIPTION,
        CanonicalEntity.INVOICE,
        CanonicalEntity.CUSTOMER,
        CanonicalEntity.PRICE,
    }
)

TIER_2_OPTIONAL_ENTITIES: frozenset[CanonicalEntity] = frozenset({CanonicalEntity.COUPON})

TIER_3_OPTIONAL_ENTITIES: frozenset[CanonicalEntity] = frozenset(
    {
        CanonicalEntity.ACCOUNT,
        CanonicalEntity.OPPORTUNITY,
        CanonicalEntity.CONTRACT,
    }
)

# Upload-time proxies: any recognized billing export satisfies the minimum requirement.
TIER_0_SOURCE_FILES: frozenset[FileType] = frozenset(
    {
        FileType.CUSTOMERS,
        FileType.SUBSCRIPTIONS,
        FileType.INVOICES,
        FileType.INVOICE_LINE_ITEMS,
        FileType.COUPONS,
        FileType.PRICE_CATALOG,
    }
)

TIER_1_RECOMMENDED_SOURCE_FILES: frozenset[FileType] = frozenset(
    {
        FileType.SUBSCRIPTIONS,
        FileType.INVOICES,
        FileType.CUSTOMERS,
        FileType.PRICE_CATALOG,
    }
)

TIER_2_OPTIONAL_SOURCE_FILES: frozenset[FileType] = frozenset({FileType.COUPONS})

TIER_3_OPTIONAL_SOURCE_FILES: frozenset[FileType] = frozenset(
    {
        FileType.CRM_ACCOUNTS,
        FileType.CRM_OPPORTUNITIES,
        FileType.CRM_CONTRACTS,
    }
)

SOURCE_FILE_TYPE_TO_ENTITIES: dict[FileType, frozenset[CanonicalEntity]] = {
    FileType.CUSTOMERS: frozenset({CanonicalEntity.CUSTOMER}),
    FileType.SUBSCRIPTIONS: frozenset({CanonicalEntity.SUBSCRIPTION}),
    FileType.INVOICES: frozenset({CanonicalEntity.INVOICE}),
    FileType.INVOICE_LINE_ITEMS: frozenset({CanonicalEntity.INVOICE_LINE_ITEM}),
    FileType.COUPONS: frozenset({CanonicalEntity.COUPON}),
    FileType.PRICE_CATALOG: frozenset({CanonicalEntity.PRICE}),
    FileType.CRM_ACCOUNTS: frozenset({CanonicalEntity.ACCOUNT}),
    FileType.CRM_OPPORTUNITIES: frozenset({CanonicalEntity.OPPORTUNITY}),
    FileType.CRM_CONTRACTS: frozenset({CanonicalEntity.CONTRACT}),
}

ENTITY_COUNT_KEYS: dict[CanonicalEntity, str] = {
    CanonicalEntity.CUSTOMER: "customers",
    CanonicalEntity.SUBSCRIPTION: "subscriptions",
    CanonicalEntity.INVOICE: "invoices",
    CanonicalEntity.INVOICE_LINE_ITEM: "invoice_line_items",
    CanonicalEntity.PRICE: "price_catalog",
    CanonicalEntity.COUPON: "coupons",
    CanonicalEntity.ACCOUNT: "crm_accounts",
    CanonicalEntity.CONTRACT: "crm_contracts",
    CanonicalEntity.OPPORTUNITY: "crm_opportunities",
}

ENTITY_LABELS: dict[CanonicalEntity, str] = {
    CanonicalEntity.CUSTOMER: "Customer",
    CanonicalEntity.SUBSCRIPTION: "Subscription",
    CanonicalEntity.INVOICE: "Invoice",
    CanonicalEntity.INVOICE_LINE_ITEM: "Invoice Line Item",
    CanonicalEntity.PRICE: "Price",
    CanonicalEntity.COUPON: "Coupon",
    CanonicalEntity.CONTRACT: "Contract",
    CanonicalEntity.ACCOUNT: "Account",
    CanonicalEntity.OPPORTUNITY: "Opportunity",
}


def entities_from_uploaded_files(uploaded: set[FileType]) -> set[CanonicalEntity]:
    entities: set[CanonicalEntity] = set()
    for file_type in uploaded:
        entities.update(SOURCE_FILE_TYPE_TO_ENTITIES.get(file_type, frozenset()))
    return entities


def entities_from_counts(counts: dict[str, int]) -> set[CanonicalEntity]:
    available: set[CanonicalEntity] = set()
    for entity, key in ENTITY_COUNT_KEYS.items():
        if counts.get(key, 0) > 0:
            available.add(entity)
    return available


def format_missing_entities(missing: set[CanonicalEntity]) -> str:
    return ", ".join(sorted(ENTITY_LABELS.get(entity, entity.value) for entity in missing))
