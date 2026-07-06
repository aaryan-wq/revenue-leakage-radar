"""Regression tests for O(1) lookup indexes on CanonicalContext."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from models import (
    Coupon,
    CrmAccount,
    CrmContract,
    Customer,
    Invoice,
    InvoiceLineItem,
    PriceCatalog,
    Subscription,
)
from verification.context import AuditContext


def _build_large_context(entity_count: int = 500) -> AuditContext:
    company_id = uuid.uuid4()
    audit_id = uuid.uuid4()
    customers: list[Customer] = []
    subscriptions: list[Subscription] = []
    invoices: list[Invoice] = []
    line_items: list[InvoiceLineItem] = []
    coupons: list[Coupon] = []
    price_catalog: list[PriceCatalog] = []
    crm_accounts: list[CrmAccount] = []
    crm_contracts: list[CrmContract] = []

    for index in range(entity_count):
        customer_id = uuid.uuid4()
        customers.append(
            Customer(
                id=customer_id,
                company_id=company_id,
                external_customer_id=f"cust_{index}",
                name=f"Customer {index}",
            )
        )
        sub_id = uuid.uuid4()
        subscriptions.append(
            Subscription(
                id=sub_id,
                customer_id=customer_id,
                external_subscription_id=f"sub_{index}",
                product_id=f"prod_{index % 10}",
                price=Decimal("100"),
                quantity=1,
                billing_interval="monthly",
                status="active",
            )
        )
        invoice_id = uuid.uuid4()
        invoices.append(
            Invoice(
                id=invoice_id,
                customer_id=customer_id,
                subscription_id=sub_id,
                external_invoice_id=f"inv_{index}",
                invoice_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                total=Decimal("100"),
            )
        )
        line_items.append(
            InvoiceLineItem(
                id=uuid.uuid4(),
                invoice_id=invoice_id,
                customer_id=customer_id,
                subscription_id=sub_id,
                external_line_item_id=f"li_{index}",
                product_id=f"prod_{index % 10}",
                unit_price=Decimal("100"),
                quantity=1,
            )
        )
        coupons.append(
            Coupon(
                id=uuid.uuid4(),
                company_id=company_id,
                code=f"PROMO{index}",
                discount_type="percent",
                discount_value=Decimal("10"),
                active=True,
            )
        )
        price_catalog.append(
            PriceCatalog(
                id=uuid.uuid4(),
                company_id=company_id,
                product_id=f"prod_{index % 10}",
                sku=f"SKU-{index % 10}",
                list_price=Decimal("100"),
                effective_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                billing_interval="monthly",
            )
        )
        crm_accounts.append(
            CrmAccount(
                id=uuid.uuid4(),
                company_id=company_id,
                customer_id=customer_id,
                external_account_id=f"acct_{index}",
                seat_count=5,
            )
        )
        crm_contracts.append(
            CrmContract(
                id=uuid.uuid4(),
                company_id=company_id,
                customer_id=customer_id,
                external_contract_id=f"contract_{index}",
                contract_price=Decimal("100"),
            )
        )

    return AuditContext(
        audit_id=audit_id,
        company_id=company_id,
        customers=customers,
        subscriptions=subscriptions,
        invoices=invoices,
        line_items=line_items,
        coupons=coupons,
        price_catalog=price_catalog,
        crm_accounts=crm_accounts,
        crm_contracts=crm_contracts,
    )


def test_entity_lookup_indexes_resolve_correctly():
    ctx = _build_large_context(50)
    customer = ctx.customers[25]
    subscription = ctx.subscriptions[25]
    invoice = ctx.invoices[25]
    coupon = ctx.coupons[25]

    assert ctx.customer_by_id(customer.id) == customer
    assert ctx.subscription_by_id(subscription.id) == subscription
    assert ctx.invoice_by_id(invoice.id) == invoice
    assert ctx.coupon_by_code(coupon.code) == coupon
    assert ctx.contracts_for_customer(customer.id)
    assert ctx.crm_account_for_customer(customer.id) is not None
    assert ctx.catalog_for_product(subscription.product_id) is not None


def test_subscription_invoices_are_pre_sorted():
    company_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    sub_id = uuid.uuid4()
    ctx = AuditContext(
        audit_id=uuid.uuid4(),
        company_id=company_id,
        customers=[
            Customer(
                id=customer_id,
                company_id=company_id,
                external_customer_id="c1",
                name="Acme",
            )
        ],
        subscriptions=[
            Subscription(
                id=sub_id,
                customer_id=customer_id,
                external_subscription_id="s1",
                product_id="prod_a",
                price=Decimal("50"),
                quantity=1,
                billing_interval="monthly",
                status="active",
            )
        ],
        invoices=[
            Invoice(
                id=uuid.uuid4(),
                customer_id=customer_id,
                subscription_id=sub_id,
                external_invoice_id="inv_late",
                invoice_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
                total=Decimal("50"),
            ),
            Invoice(
                id=uuid.uuid4(),
                customer_id=customer_id,
                subscription_id=sub_id,
                external_invoice_id="inv_early",
                invoice_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                total=Decimal("50"),
            ),
        ],
    )
    invoices = ctx.invoices_for_subscription(sub_id)
    assert invoices[0].external_invoice_id == "inv_early"
    assert invoices[1].external_invoice_id == "inv_late"
