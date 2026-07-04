import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    clerk_org_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    customers: Mapped[list["Customer"]] = relationship(back_populates="company")
    audits: Mapped[list["Audit"]] = relationship(back_populates="company")


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )
    clerk_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    session_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="created")
    platform: Mapped[str | None] = mapped_column(String(50), nullable=True)
    column_mappings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    validation_report: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    validation_result: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ingestion_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    scan_report: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    scan_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_tier: Mapped[str | None] = mapped_column(String(50), nullable=True)
    uploaded_file_types: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    available_entities: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    audit_type: Mapped[str] = mapped_column(String(32), nullable=False, default="free", index=True)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    billing_platform_detected: Mapped[str | None] = mapped_column(String(50), nullable=True)
    crm_platform_detected: Mapped[str | None] = mapped_column(String(50), nullable=True)
    csv_file_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    billing_file_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    crm_file_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    upload_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    verification_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rules_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rules_executed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rules_skipped: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rules_failed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    findings_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_monthly_leakage: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    estimated_annual_leakage: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    coverage_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    top_rule_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    report_unlocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checkout_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checkout_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    enterprise_interest_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    billing_data_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    crm_data_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    invoice_data_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    subscription_data_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    line_item_data_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    price_data_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    coupon_data_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    credit_data_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company: Mapped["Company | None"] = relationship(back_populates="audits")
    uploads: Mapped[list["Upload"]] = relationship(back_populates="audit", cascade="all, delete-orphan")
    findings: Mapped[list["Finding"]] = relationship(back_populates="audit", cascade="all, delete-orphan")
    report: Mapped["Report | None"] = relationship(back_populates="audit", uselist=False)


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    audit: Mapped["Audit"] = relationship(back_populates="uploads")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    external_customer_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    crm_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(500), nullable=True)

    company: Mapped["Company"] = relationship(back_populates="customers")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="customer")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="customer")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True
    )
    external_subscription_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    product_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plan: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    billing_interval: Mapped[str | None] = mapped_column(String(50), nullable=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    renewal_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    coupon_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="subscriptions")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="subscription")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True, index=True
    )
    external_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    invoice_number: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    invoice_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    discount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    total: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    credit_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="invoices")
    subscription: Mapped["Subscription | None"] = relationship(back_populates="invoices")
    line_items: Mapped[list["InvoiceLineItem"]] = relationship(back_populates="invoice")


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True, index=True
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True, index=True
    )
    external_line_item_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    referenced_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    product_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sku: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    extended_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    billing_interval: Mapped[str | None] = mapped_column(String(50), nullable=True)
    line_item_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_manual_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    invoice: Mapped["Invoice | None"] = relationship(back_populates="line_items")


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    discount_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    discount_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PriceCatalog(Base):
    __tablename__ = "price_catalog"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    product_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sku: Mapped[str | None] = mapped_column(String(255), nullable=True)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    effective_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    list_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    billing_interval: Mapped[str | None] = mapped_column(String(50), nullable=True)


class CrmAccount(Base):
    __tablename__ = "crm_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    external_account_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True
    )
    name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    seat_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CrmContract(Base):
    __tablename__ = "crm_contracts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    external_contract_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm_accounts.id"), nullable=True, index=True
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True
    )
    contract_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    price_increase_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_renewal_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    seat_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rule_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    customer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    product_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    expected_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    actual_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    difference: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    estimated_monthly_loss: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    estimated_arr_loss: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    calculation_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    leak_family: Mapped[str | None] = mapped_column(String(64), nullable=True)
    attribution: Mapped[str] = mapped_column(String(16), nullable=False, default="primary")
    primary_finding_ref: Mapped[str | None] = mapped_column(String(64), nullable=True)
    finding_ref: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    rule_version: Mapped[str | None] = mapped_column(String(32), nullable=True)

    audit: Mapped["Audit"] = relationship(back_populates="findings")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    recoverable_arr: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    finding_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    purchased: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    audit: Mapped["Audit"] = relationship(back_populates="report")
    purchases: Mapped[list["ReportPurchase"]] = relationship(back_populates="report")


class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="none")
    reports_remaining: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stripe_event_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReportPurchase(Base):
    __tablename__ = "report_purchases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reports.id"), nullable=True, index=True
    )
    clerk_user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(50), nullable=False)
    stripe_checkout_session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")
    receipt_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    report: Mapped["Report | None"] = relationship(back_populates="purchases")
