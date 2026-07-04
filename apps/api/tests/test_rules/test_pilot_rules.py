import uuid
from datetime import datetime, timezone
from decimal import Decimal

from models import Coupon, Customer, Invoice, InvoiceLineItem, PriceCatalog, Subscription
from verification.context import AuditContext
from verification.findings.generator import FindingGenerator
from verification.rules.billing.duplicate_subscription import rule as duplicate_rule
from verification.rules.discounts.expired_discount import rule as expired_rule
from verification.rules.pricing.price_catalog_mismatch import rule as catalog_rule


def _ctx(**kwargs) -> AuditContext:
    defaults = {
        "audit_id": uuid.uuid4(),
        "company_id": uuid.uuid4(),
    }
    defaults.update(kwargs)
    return AuditContext(**defaults)


def _evaluate(module, ctx: AuditContext):
    results = module.evaluate(ctx)
    return [
        FindingGenerator.from_rule_result(module.spec, result, audit_id=ctx.audit_id)
        for result in results
    ]


def test_expired_discount_detects_leakage():
    customer_id = uuid.uuid4()
    sub_id = uuid.uuid4()
    inv_id = uuid.uuid4()

    coupon = Coupon(
        id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        code="OLD10",
        expires_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        active=True,
    )
    sub = Subscription(
        id=sub_id,
        customer_id=customer_id,
        external_subscription_id="sub_1",
        product_id="prod_basic",
        price=Decimal("89"),
        quantity=10,
        billing_interval="monthly",
        status="active",
        coupon_id="OLD10",
    )
    invoice = Invoice(
        id=inv_id,
        customer_id=customer_id,
        subscription_id=sub_id,
        invoice_number="INV-1",
        invoice_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
        discount=Decimal("10"),
        total=Decimal("890"),
    )
    catalog = PriceCatalog(
        id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        product_id="prod_basic",
        list_price=Decimal("99"),
        effective_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    ctx = _ctx(
        subscriptions=[sub],
        invoices=[invoice],
        coupons=[coupon],
        price_catalog=[catalog],
    )
    findings = _evaluate(expired_rule, ctx)
    assert len(findings) == 1
    assert findings[0].rule_id == "expired_discount"
    assert findings[0].estimated_monthly_loss > 0


def test_price_catalog_mismatch_detects_leakage():
    customer_id = uuid.uuid4()
    inv_id = uuid.uuid4()

    invoice = Invoice(
        id=inv_id,
        customer_id=customer_id,
        invoice_number="INV-2",
        invoice_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
        total=Decimal("80"),
    )
    line = InvoiceLineItem(
        id=uuid.uuid4(),
        invoice_id=inv_id,
        product_id="prod_basic",
        sku="SKU-BASIC",
        quantity=1,
        unit_price=Decimal("80"),
    )
    catalog = PriceCatalog(
        id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        product_id="prod_basic",
        sku="SKU-BASIC",
        list_price=Decimal("99"),
        effective_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    ctx = _ctx(invoices=[invoice], line_items=[line], price_catalog=[catalog])
    findings = _evaluate(catalog_rule, ctx)
    assert len(findings) == 1
    assert findings[0].rule_id == "price_catalog_mismatch"


def test_duplicate_subscriptions_detects_leakage():
    customer_id = uuid.uuid4()
    subs = [
        Subscription(
            id=uuid.uuid4(),
            customer_id=customer_id,
            external_subscription_id="sub_a",
            product_id="prod_pro",
            price=Decimal("199"),
            billing_interval="monthly",
            status="active",
        ),
        Subscription(
            id=uuid.uuid4(),
            customer_id=customer_id,
            external_subscription_id="sub_b",
            product_id="prod_pro",
            price=Decimal("199"),
            billing_interval="monthly",
            status="active",
        ),
    ]
    ctx = _ctx(subscriptions=subs)
    findings = _evaluate(duplicate_rule, ctx)
    assert len(findings) == 1
    assert findings[0].rule_id == "duplicate_subscription"


def test_expired_discount_no_finding_when_coupon_valid():
    customer_id = uuid.uuid4()
    sub_id = uuid.uuid4()
    coupon = Coupon(
        id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        code="VALID",
        expires_at=datetime(2025, 12, 31, tzinfo=timezone.utc),
        active=True,
    )
    sub = Subscription(
        id=sub_id,
        customer_id=customer_id,
        external_subscription_id="sub_1",
        product_id="prod_basic",
        price=Decimal("89"),
        status="active",
        coupon_id="VALID",
    )
    invoice = Invoice(
        id=uuid.uuid4(),
        customer_id=customer_id,
        subscription_id=sub_id,
        invoice_number="INV-1",
        invoice_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
        discount=Decimal("10"),
    )
    ctx = _ctx(subscriptions=[sub], invoices=[invoice], coupons=[coupon])
    assert len(_evaluate(expired_rule, ctx)) == 0
