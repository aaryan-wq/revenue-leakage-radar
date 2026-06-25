"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-06-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("clerk_org_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("clerk_org_id"),
    )

    op.create_table(
        "audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("clerk_user_id", sa.String(length=255), nullable=True),
        sa.Column("session_token", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_token"),
    )
    op.create_index("ix_audits_clerk_user_id", "audits", ["clerk_user_id"])

    op.create_table(
        "uploads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=False),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("storage_path", sa.String(length=1000), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["audit_id"], ["audits.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_uploads_audit_id", "uploads", ["audit_id"])

    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_customer_id", sa.String(length=255), nullable=False),
        sa.Column("crm_id", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customers_company_id", "customers", ["company_id"])
    op.create_index("ix_customers_external_customer_id", "customers", ["external_customer_id"])

    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_subscription_id", sa.String(length=255), nullable=False),
        sa.Column("product_id", sa.String(length=255), nullable=True),
        sa.Column("plan", sa.String(length=255), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("billing_interval", sa.String(length=50), nullable=True),
        sa.Column("price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("renewal_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("coupon_id", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_subscriptions_customer_id", "subscriptions", ["customer_id"])
    op.create_index("ix_subscriptions_external_subscription_id", "subscriptions", ["external_subscription_id"])

    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("invoice_number", sa.String(length=255), nullable=False),
        sa.Column("invoice_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("subtotal", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("discount", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("total", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invoices_customer_id", "invoices", ["customer_id"])
    op.create_index("ix_invoices_subscription_id", "invoices", ["subscription_id"])
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"])

    op.create_table(
        "invoice_line_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", sa.String(length=255), nullable=True),
        sa.Column("sku", sa.String(length=255), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("unit_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("extended_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invoice_line_items_invoice_id", "invoice_line_items", ["invoice_id"])

    op.create_table(
        "coupons",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=255), nullable=False),
        sa.Column("discount_type", sa.String(length=50), nullable=True),
        sa.Column("discount_value", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_coupons_company_id", "coupons", ["company_id"])
    op.create_index("ix_coupons_code", "coupons", ["code"])

    op.create_table(
        "price_catalog",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=255), nullable=True),
        sa.Column("version", sa.String(length=50), nullable=True),
        sa.Column("effective_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("list_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_price_catalog_company_id", "price_catalog", ["company_id"])
    op.create_index("ix_price_catalog_product_id", "price_catalog", ["product_id"])

    op.create_table(
        "findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_id", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("estimated_monthly_loss", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("estimated_arr_loss", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["audit_id"], ["audits.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_findings_audit_id", "findings", ["audit_id"])
    op.create_index("ix_findings_rule_id", "findings", ["rule_id"])

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recoverable_arr", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("finding_count", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("purchased", sa.Boolean(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["audit_id"], ["audits.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("audit_id"),
    )


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("findings")
    op.drop_table("price_catalog")
    op.drop_table("coupons")
    op.drop_table("invoice_line_items")
    op.drop_table("invoices")
    op.drop_table("subscriptions")
    op.drop_table("customers")
    op.drop_table("uploads")
    op.drop_table("audits")
    op.drop_table("companies")
