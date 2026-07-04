from core.enums import FileType

CANONICAL_FIELDS: dict[FileType, list[str]] = {
    FileType.CUSTOMERS: [
        "customer_id",
        "name",
        "crm_id",
    ],
    FileType.SUBSCRIPTIONS: [
        "subscription_id",
        "customer_id",
        "product_id",
        "plan",
        "quantity",
        "billing_interval",
        "price",
        "currency",
        "start_date",
        "renewal_date",
        "status",
        "coupon_id",
    ],
    FileType.INVOICES: [
        "invoice_id",
        "customer_id",
        "subscription_id",
        "invoice_number",
        "invoice_date",
        "period_start",
        "period_end",
        "subtotal",
        "discount",
        "total",
        "currency",
        "credit_amount",
    ],
    FileType.INVOICE_LINE_ITEMS: [
        "line_item_id",
        "invoice_id",
        "customer_id",
        "subscription_id",
        "product_id",
        "sku",
        "quantity",
        "unit_price",
        "extended_price",
        "billing_interval",
        "line_item_date",
        "currency",
        "is_manual_override",
    ],
    FileType.COUPONS: [
        "coupon_id",
        "code",
        "discount_type",
        "discount_value",
        "expires_at",
        "active",
    ],
    FileType.PRICE_CATALOG: [
        "product_id",
        "sku",
        "version",
        "effective_date",
        "list_price",
        "currency",
        "billing_interval",
    ],
    FileType.CRM_ACCOUNTS: [
        "account_id",
        "customer_id",
        "name",
        "seat_count",
    ],
    FileType.CRM_OPPORTUNITIES: [
        "opportunity_id",
        "account_id",
        "renewal_price",
        "close_date",
    ],
    FileType.CRM_CONTRACTS: [
        "contract_id",
        "account_id",
        "contract_price",
        "price_increase_date",
        "expected_renewal_price",
        "start_date",
        "end_date",
        "seat_count",
    ],
}

REQUIRED_CANONICAL_FIELDS: dict[FileType, list[str]] = {
    FileType.CUSTOMERS: [
        "customer_id",
    ],
    FileType.SUBSCRIPTIONS: [
        "subscription_id",
        "customer_id",
        "status",
    ],
    FileType.INVOICES: [
        "invoice_id",
        "customer_id",
        "invoice_number",
        "total",
        "currency",
    ],
    FileType.INVOICE_LINE_ITEMS: [
        "line_item_id",
        "product_id",
        "quantity",
        "unit_price",
    ],
    FileType.COUPONS: [
        "coupon_id",
        "code",
    ],
    FileType.PRICE_CATALOG: [
        "product_id",
        "effective_date",
        "list_price",
        "currency",
    ],
}

PRIMARY_KEY_FIELDS: dict[FileType, str | list[str]] = {
    FileType.CUSTOMERS: "customer_id",
    FileType.SUBSCRIPTIONS: "subscription_id",
    FileType.INVOICES: "invoice_id",
    FileType.INVOICE_LINE_ITEMS: "line_item_id",
    FileType.COUPONS: "coupon_id",
    FileType.PRICE_CATALOG: ["product_id", "version"],
}


def primary_key_columns(file_type: FileType) -> list[str]:
    pk = PRIMARY_KEY_FIELDS.get(file_type)
    if pk is None:
        return []
    if isinstance(pk, str):
        return [pk]
    return list(pk)
