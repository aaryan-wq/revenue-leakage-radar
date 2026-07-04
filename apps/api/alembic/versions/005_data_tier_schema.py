"""Data tier schema

Revision ID: 005
Revises: 004
Create Date: 2025-06-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("audits", sa.Column("data_tier", sa.String(length=50), nullable=True))
    op.add_column(
        "audits",
        sa.Column("uploaded_file_types", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.alter_column("invoice_line_items", "invoice_id", existing_type=postgresql.UUID(), nullable=True)

    op.add_column(
        "invoice_line_items",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "invoice_line_items",
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "invoice_line_items",
        sa.Column("billing_interval", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "invoice_line_items",
        sa.Column("line_item_date", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "invoice_line_items",
        sa.Column("currency", sa.String(length=10), nullable=True),
    )
    op.create_foreign_key(
        "fk_invoice_line_items_customer_id",
        "invoice_line_items",
        "customers",
        ["customer_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_invoice_line_items_subscription_id",
        "invoice_line_items",
        "subscriptions",
        ["subscription_id"],
        ["id"],
    )
    op.create_index("ix_invoice_line_items_customer_id", "invoice_line_items", ["customer_id"])
    op.create_index("ix_invoice_line_items_subscription_id", "invoice_line_items", ["subscription_id"])

    op.add_column(
        "price_catalog",
        sa.Column("billing_interval", sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("price_catalog", "billing_interval")

    op.drop_index("ix_invoice_line_items_subscription_id", table_name="invoice_line_items")
    op.drop_index("ix_invoice_line_items_customer_id", table_name="invoice_line_items")
    op.drop_constraint("fk_invoice_line_items_subscription_id", "invoice_line_items", type_="foreignkey")
    op.drop_constraint("fk_invoice_line_items_customer_id", "invoice_line_items", type_="foreignkey")
    op.drop_column("invoice_line_items", "currency")
    op.drop_column("invoice_line_items", "line_item_date")
    op.drop_column("invoice_line_items", "billing_interval")
    op.drop_column("invoice_line_items", "subscription_id")
    op.drop_column("invoice_line_items", "customer_id")
    op.alter_column("invoice_line_items", "invoice_id", existing_type=postgresql.UUID(), nullable=False)

    op.drop_column("audits", "uploaded_file_types")
    op.drop_column("audits", "data_tier")
