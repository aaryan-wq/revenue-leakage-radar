import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

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


@dataclass
class AuditContext:
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
    has_crm: bool = False
    has_credit_data: bool = False
    has_manual_override_data: bool = False

    def customer_by_id(self, customer_id: uuid.UUID) -> Customer | None:
        return next((c for c in self.customers if c.id == customer_id), None)

    def subscriptions_for_customer(self, customer_id: uuid.UUID) -> list[Subscription]:
        return [s for s in self.subscriptions if s.customer_id == customer_id]

    def invoices_for_subscription(self, subscription_id: uuid.UUID) -> list[Invoice]:
        return [i for i in self.invoices if i.subscription_id == subscription_id]

    def line_items_for_invoice(self, invoice_id: uuid.UUID) -> list[InvoiceLineItem]:
        return [li for li in self.line_items if li.invoice_id == invoice_id]

    def coupon_by_code(self, code: str | None) -> Coupon | None:
        if not code:
            return None
        code_lower = code.lower()
        return next((c for c in self.coupons if c.code.lower() == code_lower), None)

    def catalog_for_product(
        self, product_id: str | None, sku: str | None = None, as_of: datetime | None = None
    ) -> PriceCatalog | None:
        if not product_id and not sku:
            return None
        ref = as_of or datetime.now(timezone.utc)
        matches = [
            p
            for p in self.price_catalog
            if (product_id and p.product_id == product_id) or (sku and p.sku == sku)
        ]
        if not matches:
            return None
        valid = [p for p in matches if p.effective_date is None or p.effective_date <= ref]
        pool = valid or matches
        return max(pool, key=lambda p: p.effective_date or datetime.min.replace(tzinfo=timezone.utc))

    def latest_catalog_version(self, product_id: str | None, sku: str | None = None) -> PriceCatalog | None:
        matches = [
            p
            for p in self.price_catalog
            if (product_id and p.product_id == product_id) or (sku and p.sku == sku)
        ]
        if not matches:
            return None
        return max(matches, key=lambda p: p.effective_date or datetime.min.replace(tzinfo=timezone.utc))

    def contracts_for_customer(self, customer_id: uuid.UUID) -> list[CrmContract]:
        return [c for c in self.crm_contracts if c.customer_id == customer_id]

    def crm_account_for_customer(self, customer_id: uuid.UUID) -> CrmAccount | None:
        return next((a for a in self.crm_accounts if a.customer_id == customer_id), None)


def load_audit_context(db: Session, audit_id: uuid.UUID, company_id: uuid.UUID) -> AuditContext:
    customers = db.query(Customer).filter(Customer.company_id == company_id).all()
    customer_ids = [c.id for c in customers]

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
        invoice_ids = [i.id for i in invoices]
        if invoice_ids:
            line_items = db.query(InvoiceLineItem).filter(InvoiceLineItem.invoice_id.in_(invoice_ids)).all()

    coupons = db.query(Coupon).filter(Coupon.company_id == company_id).all()
    price_catalog = db.query(PriceCatalog).filter(PriceCatalog.company_id == company_id).all()
    crm_accounts = db.query(CrmAccount).filter(CrmAccount.company_id == company_id).all()
    crm_contracts = db.query(CrmContract).filter(CrmContract.company_id == company_id).all()

    has_credit = any(i.credit_amount is not None for i in invoices)
    has_manual = any(li.is_manual_override for li in line_items)

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
        has_crm=bool(crm_accounts or crm_contracts),
        has_credit_data=has_credit,
        has_manual_override_data=has_manual,
    )
