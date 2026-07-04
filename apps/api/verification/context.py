from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from core.canonical_entities import CanonicalEntity, entities_from_uploaded_files
from core.data_tiers import get_audit_data_tier_from_entities
from core.enums import DataTier, FileType
from models import (
    Audit,
    Coupon,
    CrmAccount,
    CrmContract,
    Customer,
    Invoice,
    InvoiceLineItem,
    PriceCatalog,
    Subscription,
)

ACTIVE_SUBSCRIPTION_STATUSES = frozenset({"active", "trialing", "past_due"})

ENTITY_FIELD_SOURCES: dict[CanonicalEntity, tuple[str, ...]] = {
    CanonicalEntity.CUSTOMER: ("customers",),
    CanonicalEntity.SUBSCRIPTION: ("subscriptions",),
    CanonicalEntity.INVOICE: ("invoices",),
    CanonicalEntity.INVOICE_LINE_ITEM: ("line_items",),
    CanonicalEntity.PRICE: ("price_catalog",),
    CanonicalEntity.COUPON: ("coupons",),
    CanonicalEntity.ACCOUNT: ("crm_accounts",),
    CanonicalEntity.CONTRACT: ("crm_contracts",),
}

FIELD_GETTERS: dict[tuple[str, str], str] = {
    ("customer", "customer_id"): "external_customer_id",
    ("subscription", "subscription_id"): "external_subscription_id",
    ("subscription", "customer_id"): "customer_id",
    ("subscription", "product_id"): "product_id",
    ("subscription", "price"): "price",
    ("subscription", "quantity"): "quantity",
    ("subscription", "billing_interval"): "billing_interval",
    ("subscription", "status"): "status",
    ("subscription", "coupon_id"): "coupon_id",
    ("subscription", "currency"): "currency",
    ("subscription", "start_date"): "start_date",
    ("subscription", "renewal_date"): "renewal_date",
    ("invoice", "invoice_id"): "external_invoice_id",
    ("invoice", "customer_id"): "customer_id",
    ("invoice", "subscription_id"): "subscription_id",
    ("invoice", "invoice_date"): "invoice_date",
    ("invoice", "period_start"): "period_start",
    ("invoice", "period_end"): "period_end",
    ("invoice", "subtotal"): "subtotal",
    ("invoice", "discount"): "discount",
    ("invoice", "total"): "total",
    ("invoice", "currency"): "currency",
    ("invoice", "credit_amount"): "credit_amount",
    ("invoice_line_item", "line_item_id"): "external_line_item_id",
    ("invoice_line_item", "invoice_id"): "invoice_id",
    ("invoice_line_item", "subscription_id"): "subscription_id",
    ("invoice_line_item", "product_id"): "product_id",
    ("invoice_line_item", "unit_price"): "unit_price",
    ("invoice_line_item", "quantity"): "quantity",
    ("invoice_line_item", "billing_interval"): "billing_interval",
    ("invoice_line_item", "is_manual_override"): "is_manual_override",
    ("invoice_line_item", "sku"): "sku",
    ("price", "product_id"): "product_id",
    ("price", "list_price"): "list_price",
    ("price", "effective_date"): "effective_date",
    ("price", "billing_interval"): "billing_interval",
    ("price", "currency"): "currency",
    ("price", "sku"): "sku",
    ("coupon", "coupon_id"): "code",
    ("coupon", "code"): "code",
    ("coupon", "expires_at"): "expires_at",
    ("coupon", "discount_type"): "discount_type",
    ("coupon", "discount_value"): "discount_value",
    ("coupon", "active"): "active",
    ("contract", "contract_id"): "external_contract_id",
    ("contract", "customer_id"): "customer_id",
    ("contract", "contract_price"): "contract_price",
    ("contract", "price_increase_date"): "price_increase_date",
    ("contract", "expected_renewal_price"): "expected_renewal_price",
    ("contract", "end_date"): "end_date",
    ("account", "account_id"): "external_account_id",
    ("account", "customer_id"): "customer_id",
    ("account", "seat_count"): "seat_count",
}


def is_active_subscription(status: str | None) -> bool:
    return (status or "").lower() in ACTIVE_SUBSCRIPTION_STATUSES


@dataclass
class CanonicalContext:
    audit_id: uuid.UUID
    company_id: uuid.UUID
    customers: list[Customer] = field(default_factory=list)
    subscriptions: list[Subscription] = field(default_factory=list)
    invoices: list[Invoice] = field(default_factory=list)
    line_items: list[InvoiceLineItem] = field(default_factory=list)
    coupons: list[Coupon] = field(default_factory=list)
    price_catalog: list[PriceCatalog] = field(default_factory=list)
    crm_accounts: list[CrmAccount] = field(default_factory=list)
    crm_contracts: list[CrmContract] = field(default_factory=list)
    uploaded_file_types: set[FileType] = field(default_factory=set)
    available_entities: set[CanonicalEntity] = field(default_factory=set)
    data_tier: DataTier = DataTier.INSUFFICIENT
    entity_coverage: dict[str, bool] = field(default_factory=dict)
    has_crm: bool = False
    has_credit_data: bool = False
    has_manual_override_data: bool = False
    anchor_date: datetime = field(default_factory=lambda: datetime(1970, 1, 1, tzinfo=timezone.utc))
    _by_customer: dict[uuid.UUID, list[Subscription]] = field(default_factory=dict, init=False, repr=False)
    _by_subscription_invoices: dict[uuid.UUID, list[Invoice]] = field(default_factory=dict, init=False, repr=False)
    _by_invoice_line_items: dict[uuid.UUID, list[InvoiceLineItem]] = field(default_factory=dict, init=False, repr=False)
    _latest_line_by_subscription: dict[uuid.UUID, tuple[InvoiceLineItem, Invoice | None, datetime]] = field(
        default_factory=dict, init=False, repr=False
    )
    _latest_line_by_product: dict[str, tuple[InvoiceLineItem, Invoice | None, datetime]] = field(
        default_factory=dict, init=False, repr=False
    )
    _field_availability: set[tuple[str, str]] = field(default_factory=set, init=False, repr=False)
    _product_ids: set[str] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self) -> None:
        self._build_indexes()

    @property
    def reference_date(self) -> datetime:
        """Latest invoice or line-item date in the dataset, deterministic audit anchor."""
        candidates: list[datetime] = []
        for invoice in self.invoices:
            if invoice.invoice_date:
                candidates.append(invoice.invoice_date)
        for line_item in self.line_items:
            if line_item.line_item_date:
                candidates.append(line_item.line_item_date)
        if not candidates:
            ref = self.anchor_date
            if ref.tzinfo is None:
                ref = ref.replace(tzinfo=timezone.utc)
            return ref
        ref = max(candidates)
        if ref.tzinfo is None:
            ref = ref.replace(tzinfo=timezone.utc)
        return ref

    def _build_indexes(self) -> None:
        for sub in self.subscriptions:
            self._by_customer.setdefault(sub.customer_id, []).append(sub)
            if sub.product_id:
                self._product_ids.add(sub.product_id)

        for invoice in self.invoices:
            if invoice.subscription_id:
                self._by_subscription_invoices.setdefault(invoice.subscription_id, []).append(invoice)

        for line_item in self.line_items:
            if line_item.invoice_id:
                self._by_invoice_line_items.setdefault(line_item.invoice_id, []).append(line_item)
            if line_item.product_id:
                self._product_ids.add(line_item.product_id)

            invoice = self.invoice_by_id(line_item.invoice_id) if line_item.invoice_id else None
            subscription_id = line_item.subscription_id or (invoice.subscription_id if invoice else None)
            as_of = line_item.line_item_date
            if as_of is None and invoice and invoice.invoice_date:
                as_of = invoice.invoice_date
            if as_of is None:
                as_of = self.anchor_date
            if as_of.tzinfo is None:
                as_of = as_of.replace(tzinfo=timezone.utc)

            if subscription_id:
                existing = self._latest_line_by_subscription.get(subscription_id)
                if existing is None or as_of > existing[2]:
                    self._latest_line_by_subscription[subscription_id] = (line_item, invoice, as_of)

            if line_item.product_id:
                existing = self._latest_line_by_product.get(line_item.product_id)
                if existing is None or as_of > existing[2]:
                    self._latest_line_by_product[line_item.product_id] = (line_item, invoice, as_of)

        self._field_availability = self._compute_field_availability()

    def _compute_field_availability(self) -> set[tuple[str, str]]:
        available: set[tuple[str, str]] = set()
        collections: dict[str, list] = {
            "customer": self.customers,
            "subscription": self.subscriptions,
            "invoice": self.invoices,
            "invoice_line_item": self.line_items,
            "price": self.price_catalog,
            "coupon": self.coupons,
            "contract": self.crm_contracts,
            "account": self.crm_accounts,
        }
        for (entity, field_name), attr in FIELD_GETTERS.items():
            rows = collections.get(entity, [])
            for row in rows:
                value = getattr(row, attr, None)
                if value is not None and value != "":
                    available.add((entity, field_name))
                    break
        return available

    def field_availability(self) -> set[tuple[str, str]]:
        return set(self._field_availability)

    def available_entities_set(self) -> set[CanonicalEntity]:
        return set(self.available_entities)

    def has_entity(self, entity: CanonicalEntity) -> bool:
        return entity in self.available_entities

    def product_ids(self) -> set[str]:
        return set(self._product_ids)

    def customer_by_id(self, customer_id: uuid.UUID) -> Customer | None:
        return next((customer for customer in self.customers if customer.id == customer_id), None)

    def subscription_by_id(self, subscription_id: uuid.UUID) -> Subscription | None:
        return next((sub for sub in self.subscriptions if sub.id == subscription_id), None)

    def invoice_by_id(self, invoice_id: uuid.UUID | None) -> Invoice | None:
        if not invoice_id:
            return None
        return next((invoice for invoice in self.invoices if invoice.id == invoice_id), None)

    def subscriptions_for_customer(self, customer_id: uuid.UUID) -> list[Subscription]:
        return list(self._by_customer.get(customer_id, []))

    def invoices_for_subscription(self, subscription_id: uuid.UUID) -> list[Invoice]:
        return list(self._by_subscription_invoices.get(subscription_id, []))

    def line_items_for_invoice(self, invoice_id: uuid.UUID) -> list[InvoiceLineItem]:
        return list(self._by_invoice_line_items.get(invoice_id, []))

    def latest_line_item_for_subscription(
        self, subscription_id: uuid.UUID
    ) -> tuple[InvoiceLineItem, Invoice | None, datetime] | None:
        return self._latest_line_by_subscription.get(subscription_id)

    def latest_line_item_for_product(self, product_id: str) -> tuple[InvoiceLineItem, Invoice | None, datetime] | None:
        return self._latest_line_by_product.get(product_id)

    def coupon_by_code(self, code: str | None) -> Coupon | None:
        if not code:
            return None
        code_lower = code.lower()
        return next((coupon for coupon in self.coupons if coupon.code.lower() == code_lower), None)

    def catalog_for_product(
        self, product_id: str | None, sku: str | None = None, as_of: datetime | None = None
    ) -> PriceCatalog | None:
        if not product_id and not sku:
            return None
        ref = as_of or self.reference_date
        if product_id:
            matches = [entry for entry in self.price_catalog if entry.product_id == product_id]
        else:
            matches = [entry for entry in self.price_catalog if entry.sku == sku]
        if not matches:
            return None
        valid = [entry for entry in matches if entry.effective_date is None or entry.effective_date <= ref]
        pool = valid or matches
        return max(pool, key=lambda entry: entry.effective_date or datetime.min.replace(tzinfo=timezone.utc))

    def latest_catalog_version(self, product_id: str | None, sku: str | None = None) -> PriceCatalog | None:
        if product_id:
            matches = [entry for entry in self.price_catalog if entry.product_id == product_id]
        elif sku:
            matches = [entry for entry in self.price_catalog if entry.sku == sku]
        else:
            matches = []
        if not matches:
            return None
        return max(matches, key=lambda entry: entry.effective_date or datetime.min.replace(tzinfo=timezone.utc))

    def contracts_for_customer(self, customer_id: uuid.UUID) -> list[CrmContract]:
        return [contract for contract in self.crm_contracts if contract.customer_id == customer_id]

    def crm_account_for_customer(self, customer_id: uuid.UUID) -> CrmAccount | None:
        return next((account for account in self.crm_accounts if account.customer_id == customer_id), None)

    def has_multiple_invoices_for_any_subscription(self) -> bool:
        return any(len(invoices) >= 2 for invoices in self._by_subscription_invoices.values())


AuditContext = CanonicalContext


def _derive_entities_from_rows(
    customers: list[Customer],
    subscriptions: list[Subscription],
    invoices: list[Invoice],
    line_items: list[InvoiceLineItem],
    coupons: list[Coupon],
    price_catalog: list[PriceCatalog],
    crm_accounts: list[CrmAccount],
    crm_contracts: list[CrmContract],
) -> set[CanonicalEntity]:
    available: set[CanonicalEntity] = set()
    if customers:
        available.add(CanonicalEntity.CUSTOMER)
    if subscriptions:
        available.add(CanonicalEntity.SUBSCRIPTION)
    if invoices:
        available.add(CanonicalEntity.INVOICE)
    if line_items:
        available.add(CanonicalEntity.INVOICE_LINE_ITEM)
    if coupons:
        available.add(CanonicalEntity.COUPON)
    if price_catalog:
        available.add(CanonicalEntity.PRICE)
    if crm_accounts:
        available.add(CanonicalEntity.ACCOUNT)
    if crm_contracts:
        available.add(CanonicalEntity.CONTRACT)
    return available


def load_audit_context(db: Session, audit_id: uuid.UUID, company_id: uuid.UUID) -> CanonicalContext:
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    uploaded_file_types: set[FileType] = set()
    if audit and audit.uploaded_file_types:
        uploaded_file_types = {FileType(file_type) for file_type in audit.uploaded_file_types}
    elif audit:
        uploaded_file_types = {FileType(upload.file_type) for upload in audit.uploads if upload.status == "uploaded"}

    customers = db.query(Customer).filter(Customer.company_id == company_id).all()
    customer_ids = [customer.id for customer in customers]

    subscriptions: list[Subscription] = []
    invoices: list[Invoice] = []
    line_items: list[InvoiceLineItem] = []

    if customer_ids:
        subscriptions = db.query(Subscription).filter(Subscription.customer_id.in_(customer_ids)).all()
        invoices = (
            db.query(Invoice)
            .options(joinedload(Invoice.line_items))
            .filter(Invoice.customer_id.in_(customer_ids))
            .all()
        )
        invoice_ids = [invoice.id for invoice in invoices]
        if invoice_ids or customer_ids:
            filters = []
            if invoice_ids:
                filters.append(InvoiceLineItem.invoice_id.in_(invoice_ids))
            if customer_ids:
                filters.append(InvoiceLineItem.customer_id.in_(customer_ids))
            line_items = db.query(InvoiceLineItem).filter(or_(*filters)).all()

    coupons = db.query(Coupon).filter(Coupon.company_id == company_id).all()
    price_catalog = db.query(PriceCatalog).filter(PriceCatalog.company_id == company_id).all()
    crm_accounts = db.query(CrmAccount).filter(CrmAccount.company_id == company_id).all()
    crm_contracts = db.query(CrmContract).filter(CrmContract.company_id == company_id).all()

    has_credit = any(invoice.credit_amount is not None for invoice in invoices)
    has_manual = any(line_item.is_manual_override for line_item in line_items)

    if audit and audit.available_entities:
        available_entities = {CanonicalEntity(entity) for entity in audit.available_entities}
    else:
        available_entities = _derive_entities_from_rows(
            customers,
            subscriptions,
            invoices,
            line_items,
            coupons,
            price_catalog,
            crm_accounts,
            crm_contracts,
        )
        if not available_entities and uploaded_file_types:
            available_entities = entities_from_uploaded_files(uploaded_file_types)

    data_tier = get_audit_data_tier_from_entities(available_entities)
    entity_coverage = {entity.value: entity in available_entities for entity in CanonicalEntity}

    anchor = audit.created_at if audit and audit.created_at else datetime(1970, 1, 1, tzinfo=timezone.utc)
    if anchor.tzinfo is None:
        anchor = anchor.replace(tzinfo=timezone.utc)

    return CanonicalContext(
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
        uploaded_file_types=uploaded_file_types,
        available_entities=available_entities,
        data_tier=data_tier,
        entity_coverage=entity_coverage,
        has_crm=bool(crm_accounts or crm_contracts),
        has_credit_data=has_credit,
        has_manual_override_data=has_manual,
        anchor_date=anchor,
    )
