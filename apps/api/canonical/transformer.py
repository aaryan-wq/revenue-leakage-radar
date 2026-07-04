import logging
import uuid

from sqlalchemy.orm import Session

from canonical.errors import RowError, TransformResult
from canonical.utils import parse_bool, parse_date, parse_decimal, parse_int, safe_str
from core.enums import AuditStatus, FileType, Platform
from ingestion.types import IngestionContext
from models import (
    Audit,
    Company,
    Coupon,
    CrmAccount,
    CrmContract,
    Customer,
    Invoice,
    InvoiceLineItem,
    PriceCatalog,
    Subscription,
)

logger = logging.getLogger(__name__)


def ensure_company(db: Session, audit: Audit) -> Company:
    if audit.company_id:
        company = db.query(Company).filter(Company.id == audit.company_id).first()
        if company:
            return company

    company = Company(name=f"Audit {str(audit.id)[:8]}")
    db.add(company)
    db.flush()
    audit.company_id = company.id
    db.commit()
    db.refresh(audit)
    return company


def clear_canonical_data(db: Session, company_id: uuid.UUID) -> None:
    customers = db.query(Customer).filter(Customer.company_id == company_id).all()
    customer_ids = [c.id for c in customers]

    if customer_ids:
        subscriptions = db.query(Subscription).filter(Subscription.customer_id.in_(customer_ids)).all()
        sub_ids = [s.id for s in subscriptions]

        if sub_ids:
            invoices = db.query(Invoice).filter(Invoice.subscription_id.in_(sub_ids)).all()
        else:
            invoices = db.query(Invoice).filter(Invoice.customer_id.in_(customer_ids)).all()

        invoice_ids = [i.id for i in invoices]
        if invoice_ids:
            db.query(InvoiceLineItem).filter(InvoiceLineItem.invoice_id.in_(invoice_ids)).delete(
                synchronize_session=False
            )
        db.query(InvoiceLineItem).filter(InvoiceLineItem.customer_id.in_(customer_ids)).delete(
            synchronize_session=False
        )
        if invoice_ids:
            db.query(Invoice).filter(Invoice.id.in_(invoice_ids)).delete(synchronize_session=False)

        db.query(Subscription).filter(Subscription.customer_id.in_(customer_ids)).delete(synchronize_session=False)
        db.query(Customer).filter(Customer.id.in_(customer_ids)).delete(synchronize_session=False)

    db.query(Coupon).filter(Coupon.company_id == company_id).delete(synchronize_session=False)
    db.query(PriceCatalog).filter(PriceCatalog.company_id == company_id).delete(synchronize_session=False)
    db.query(CrmContract).filter(CrmContract.company_id == company_id).delete(synchronize_session=False)
    db.query(CrmAccount).filter(CrmAccount.company_id == company_id).delete(synchronize_session=False)
    db.commit()


def _ensure_customer(
    db: Session,
    company_id: uuid.UUID,
    customer_map: dict[str, uuid.UUID],
    external_id: str,
    name: str | None = None,
    crm_id: str | None = None,
) -> uuid.UUID:
    if external_id in customer_map:
        return customer_map[external_id]

    customer = Customer(
        company_id=company_id,
        external_customer_id=external_id,
        name=name or external_id,
        crm_id=crm_id,
    )
    db.add(customer)
    db.flush()
    customer_map[external_id] = customer.id
    return customer.id


def transform_customers(
    db: Session,
    company_id: uuid.UUID,
    ctx: IngestionContext,
    result: TransformResult,
) -> dict[str, uuid.UUID]:
    customer_map: dict[str, uuid.UUID] = {}

    customers_df = ctx.frames.get(FileType.CUSTOMERS)
    if customers_df is not None:
        for idx, row in enumerate(customers_df.iter_rows(named=True)):
            external_id = safe_str(row.get("customer_id"))
            if not external_id:
                result.row_errors.append(RowError(FileType.CUSTOMERS.value, idx, "Missing customer_id"))
                continue
            _ensure_customer(
                db,
                company_id,
                customer_map,
                external_id,
                name=safe_str(row.get("name")),
                crm_id=safe_str(row.get("crm_id")),
            )

    subs_df = ctx.frames.get(FileType.SUBSCRIPTIONS)
    if subs_df is not None and "customer_id" in subs_df.columns:
        for idx, row in enumerate(subs_df.iter_rows(named=True)):
            external_id = safe_str(row.get("customer_id"))
            if not external_id:
                result.row_errors.append(
                    RowError(FileType.SUBSCRIPTIONS.value, idx, "Missing customer_id")
                )
                continue
            _ensure_customer(
                db,
                company_id,
                customer_map,
                external_id,
            )

    li_df = ctx.frames.get(FileType.INVOICE_LINE_ITEMS)
    if li_df is not None and "customer_id" in li_df.columns:
        for idx, row in enumerate(li_df.iter_rows(named=True)):
            external_id = safe_str(row.get("customer_id"))
            if not external_id:
                continue
            _ensure_customer(db, company_id, customer_map, external_id)

    result.counts["customers"] = len(customer_map)
    return customer_map


def transform_subscriptions(
    db: Session,
    customer_map: dict[str, uuid.UUID],
    ctx: IngestionContext,
    result: TransformResult,
) -> dict[str, uuid.UUID]:
    sub_map: dict[str, uuid.UUID] = {}
    subs_df = ctx.frames.get(FileType.SUBSCRIPTIONS)
    if subs_df is None:
        return sub_map

    for idx, row in enumerate(subs_df.iter_rows(named=True)):
        external_sub_id = safe_str(row.get("subscription_id"))
        customer_ext = safe_str(row.get("customer_id"))
        if not external_sub_id or not customer_ext:
            result.row_errors.append(
                RowError(FileType.SUBSCRIPTIONS.value, idx, "Missing subscription_id or customer_id")
            )
            continue

        customer_id = customer_map.get(customer_ext)
        if not customer_id:
            result.row_errors.append(
                RowError(FileType.SUBSCRIPTIONS.value, idx, f"Unknown customer_id: {customer_ext}")
            )
            continue

        subscription = Subscription(
            customer_id=customer_id,
            external_subscription_id=external_sub_id,
            product_id=safe_str(row.get("product_id")),
            plan=safe_str(row.get("plan")),
            quantity=parse_int(row.get("quantity")),
            billing_interval=safe_str(row.get("billing_interval")),
            price=parse_decimal(row.get("price")),
            currency=safe_str(row.get("currency")),
            start_date=parse_date(row.get("start_date")),
            renewal_date=parse_date(row.get("renewal_date")),
            status=safe_str(row.get("status")),
            coupon_id=safe_str(row.get("coupon_id")),
        )
        db.add(subscription)
        db.flush()
        sub_map[external_sub_id] = subscription.id

    result.counts["subscriptions"] = len(sub_map)
    return sub_map


def transform_invoices(
    db: Session,
    customer_map: dict[str, uuid.UUID],
    sub_map: dict[str, uuid.UUID],
    ctx: IngestionContext,
    result: TransformResult,
) -> dict[str, uuid.UUID]:
    invoice_map: dict[str, uuid.UUID] = {}
    inv_df = ctx.frames.get(FileType.INVOICES)
    if inv_df is None:
        return invoice_map

    for idx, row in enumerate(inv_df.iter_rows(named=True)):
        invoice_ext = safe_str(row.get("invoice_id"))
        customer_ext = safe_str(row.get("customer_id"))
        invoice_number = safe_str(row.get("invoice_number")) or invoice_ext

        if not invoice_ext or not customer_ext or not invoice_number:
            result.row_errors.append(
                RowError(FileType.INVOICES.value, idx, "Missing invoice_id, customer_id, or invoice_number")
            )
            continue

        customer_id = customer_map.get(customer_ext)
        if not customer_id:
            result.row_errors.append(
                RowError(FileType.INVOICES.value, idx, f"Unknown customer_id: {customer_ext}")
            )
            continue

        sub_ext = safe_str(row.get("subscription_id"))
        subscription_id = sub_map.get(sub_ext) if sub_ext else None

        invoice = Invoice(
            customer_id=customer_id,
            subscription_id=subscription_id,
            external_invoice_id=invoice_ext,
            invoice_number=invoice_number,
            invoice_date=parse_date(row.get("invoice_date")),
            period_start=parse_date(row.get("period_start")),
            period_end=parse_date(row.get("period_end")),
            subtotal=parse_decimal(row.get("subtotal")),
            discount=parse_decimal(row.get("discount")),
            total=parse_decimal(row.get("total")),
            credit_amount=parse_decimal(row.get("credit_amount")),
            currency=safe_str(row.get("currency")),
        )
        db.add(invoice)
        db.flush()
        invoice_map[invoice_ext] = invoice.id

    result.counts["invoices"] = len(invoice_map)
    return invoice_map


def ensure_stub_invoices(
    db: Session,
    company_id: uuid.UUID,
    customer_map: dict[str, uuid.UUID],
    invoice_map: dict[str, uuid.UUID],
    ctx: IngestionContext,
    result: TransformResult,
) -> dict[str, uuid.UUID]:
    """Create minimal invoice stubs from line items when invoices.csv is absent."""
    if FileType.INVOICES in ctx.uploaded_file_types:
        return invoice_map

    li_df = ctx.frames.get(FileType.INVOICE_LINE_ITEMS)
    if li_df is None:
        return invoice_map

    stub_customer_ext = "__tier0_stub_customer__"
    stub_customer_id = _ensure_customer(db, company_id, customer_map, stub_customer_ext, name="Unknown Customer")

    stubs_before = len(invoice_map)

    for idx, row in enumerate(li_df.iter_rows(named=True)):
        invoice_ext = safe_str(row.get("invoice_id"))
        if not invoice_ext or invoice_ext in invoice_map:
            continue

        customer_ext = safe_str(row.get("customer_id"))
        customer_id = customer_map.get(customer_ext) if customer_ext else stub_customer_id
        if customer_ext and customer_ext not in customer_map:
            customer_id = _ensure_customer(db, company_id, customer_map, customer_ext)

        invoice = Invoice(
            customer_id=customer_id,
            subscription_id=None,
            external_invoice_id=invoice_ext,
            invoice_number=invoice_ext,
            invoice_date=parse_date(row.get("line_item_date")),
            currency=safe_str(row.get("currency")),
        )
        db.add(invoice)
        db.flush()
        invoice_map[invoice_ext] = invoice.id

    stubs_created = len(invoice_map) - stubs_before
    if stubs_created:
        result.counts["stub_invoices"] = stubs_created

    return invoice_map


def transform_line_items(
    db: Session,
    invoice_map: dict[str, uuid.UUID],
    customer_map: dict[str, uuid.UUID],
    sub_map: dict[str, uuid.UUID],
    company_id: uuid.UUID,
    ctx: IngestionContext,
    result: TransformResult,
) -> None:
    li_df = ctx.frames.get(FileType.INVOICE_LINE_ITEMS)
    if li_df is None:
        return

    count = 0
    for idx, row in enumerate(li_df.iter_rows(named=True)):
        invoice_ext = safe_str(row.get("invoice_id"))
        invoice_id = invoice_map.get(invoice_ext) if invoice_ext else None
        referenced_invoice_id = invoice_ext if invoice_ext and invoice_id is None else None

        customer_ext = safe_str(row.get("customer_id"))
        customer_id = customer_map.get(customer_ext) if customer_ext else None
        if customer_ext and not customer_id:
            customer_id = _ensure_customer(db, company_id, customer_map, customer_ext)

        sub_ext = safe_str(row.get("subscription_id"))
        subscription_id = sub_map.get(sub_ext) if sub_ext else None

        if not invoice_id and not customer_id:
            result.row_errors.append(
                RowError(
                    FileType.INVOICE_LINE_ITEMS.value,
                    idx,
                    "Line item requires invoice_id or customer_id",
                )
            )
            continue

        line_item = InvoiceLineItem(
            invoice_id=invoice_id,
            referenced_invoice_id=referenced_invoice_id,
            customer_id=customer_id,
            subscription_id=subscription_id,
            external_line_item_id=safe_str(row.get("line_item_id")),
            product_id=safe_str(row.get("product_id")),
            sku=safe_str(row.get("sku")),
            quantity=parse_int(row.get("quantity")),
            unit_price=parse_decimal(row.get("unit_price")),
            extended_price=parse_decimal(row.get("extended_price")),
            billing_interval=safe_str(row.get("billing_interval")),
            line_item_date=parse_date(row.get("line_item_date")),
            currency=safe_str(row.get("currency")),
            is_manual_override=parse_bool(row.get("is_manual_override")) or False,
        )
        db.add(line_item)
        count += 1

    db.flush()
    result.counts["invoice_line_items"] = count


def transform_coupons(db: Session, company_id: uuid.UUID, ctx: IngestionContext, result: TransformResult) -> None:
    coupons_df = ctx.frames.get(FileType.COUPONS)
    if coupons_df is None:
        return

    count = 0
    for idx, row in enumerate(coupons_df.iter_rows(named=True)):
        code = safe_str(row.get("code"))
        if not code:
            result.row_errors.append(RowError(FileType.COUPONS.value, idx, "Missing coupon code"))
            continue

        coupon = Coupon(
            company_id=company_id,
            code=code,
            discount_type=safe_str(row.get("discount_type")),
            discount_value=parse_decimal(row.get("discount_value")),
            expires_at=parse_date(row.get("expires_at")),
            active=parse_bool(row.get("active")),
        )
        db.add(coupon)
        count += 1

    db.flush()
    result.counts["coupons"] = count


def transform_price_catalog(
    db: Session, company_id: uuid.UUID, ctx: IngestionContext, result: TransformResult
) -> None:
    catalog_df = ctx.frames.get(FileType.PRICE_CATALOG)
    if catalog_df is None:
        return

    count = 0
    for idx, row in enumerate(catalog_df.iter_rows(named=True)):
        product_id = safe_str(row.get("product_id"))
        if not product_id:
            result.row_errors.append(RowError(FileType.PRICE_CATALOG.value, idx, "Missing product_id"))
            continue

        entry = PriceCatalog(
            company_id=company_id,
            product_id=product_id,
            sku=safe_str(row.get("sku")),
            version=safe_str(row.get("version")),
            effective_date=parse_date(row.get("effective_date")),
            list_price=parse_decimal(row.get("list_price")),
            currency=safe_str(row.get("currency")),
            billing_interval=safe_str(row.get("billing_interval")),
        )
        db.add(entry)
        count += 1

    db.flush()
    result.counts["price_catalog"] = count


def transform_crm_accounts(
    db: Session,
    company_id: uuid.UUID,
    customer_map: dict[str, uuid.UUID],
    ctx: IngestionContext,
    result: TransformResult,
) -> dict[str, uuid.UUID]:
    account_map: dict[str, uuid.UUID] = {}
    df = ctx.frames.get(FileType.CRM_ACCOUNTS)
    if df is None:
        return account_map

    for idx, row in enumerate(df.iter_rows(named=True)):
        ext_id = safe_str(row.get("account_id"))
        if not ext_id:
            result.row_errors.append(RowError(FileType.CRM_ACCOUNTS.value, idx, "Missing account_id"))
            continue

        customer_ext = safe_str(row.get("customer_id"))
        customer_id = customer_map.get(customer_ext) if customer_ext else None

        account = CrmAccount(
            company_id=company_id,
            external_account_id=ext_id,
            customer_id=customer_id,
            name=safe_str(row.get("name")),
            seat_count=parse_int(row.get("seat_count")),
        )
        db.add(account)
        db.flush()
        account_map[ext_id] = account.id

    result.counts["crm_accounts"] = len(account_map)
    return account_map


def transform_crm_contracts(
    db: Session,
    company_id: uuid.UUID,
    customer_map: dict[str, uuid.UUID],
    account_map: dict[str, uuid.UUID],
    ctx: IngestionContext,
    result: TransformResult,
) -> None:
    df = ctx.frames.get(FileType.CRM_CONTRACTS)
    if df is None:
        return

    count = 0
    for idx, row in enumerate(df.iter_rows(named=True)):
        ext_id = safe_str(row.get("contract_id"))
        if not ext_id:
            result.row_errors.append(RowError(FileType.CRM_CONTRACTS.value, idx, "Missing contract_id"))
            continue

        account_ext = safe_str(row.get("account_id"))
        account_id = account_map.get(account_ext) if account_ext else None
        customer_id = None
        if account_id:
            account = db.query(CrmAccount).filter(CrmAccount.id == account_id).first()
            if account:
                customer_id = account.customer_id

        contract = CrmContract(
            company_id=company_id,
            external_contract_id=ext_id,
            account_id=account_id,
            customer_id=customer_id,
            contract_price=parse_decimal(row.get("contract_price")),
            price_increase_date=parse_date(row.get("price_increase_date")),
            expected_renewal_price=parse_decimal(row.get("expected_renewal_price")),
            start_date=parse_date(row.get("start_date")),
            end_date=parse_date(row.get("end_date")),
            seat_count=parse_int(row.get("seat_count")),
        )
        db.add(contract)
        count += 1

    db.flush()
    result.counts["crm_contracts"] = count


def run_canonical_transform(db: Session, audit: Audit, ctx: IngestionContext) -> TransformResult:
    result = TransformResult()
    company = ensure_company(db, audit)
    clear_canonical_data(db, company.id)

    customer_map = transform_customers(db, company.id, ctx, result)
    sub_map = transform_subscriptions(db, customer_map, ctx, result)
    invoice_map = transform_invoices(db, customer_map, sub_map, ctx, result)
    invoice_map = ensure_stub_invoices(db, company.id, customer_map, invoice_map, ctx, result)
    transform_line_items(db, invoice_map, customer_map, sub_map, company.id, ctx, result)
    transform_coupons(db, company.id, ctx, result)
    transform_price_catalog(db, company.id, ctx, result)
    account_map = transform_crm_accounts(db, company.id, customer_map, ctx, result)
    transform_crm_contracts(db, company.id, customer_map, account_map, ctx, result)

    db.commit()
    return result


def run_ingestion_pipeline(db: Session, audit: Audit) -> None:
    """Backward-compatible entrypoint, orchestration lives in ingestion.pipeline."""
    from ingestion.pipeline import run_ingestion_pipeline as _run

    _run(db, audit)
