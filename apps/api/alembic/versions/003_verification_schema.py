"""Verification schema extensions

Revision ID: 003
Revises: 002
Create Date: 2025-06-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("audits", sa.Column("scan_report", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("audits", sa.Column("scan_error", sa.Text(), nullable=True))

    op.add_column("invoices", sa.Column("external_invoice_id", sa.String(length=255), nullable=True))
    op.add_column("invoices", sa.Column("credit_amount", sa.Numeric(precision=18, scale=4), nullable=True))

    op.add_column("invoice_line_items", sa.Column("external_line_item_id", sa.String(length=255), nullable=True))
    op.add_column(
        "invoice_line_items",
        sa.Column("is_manual_override", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "crm_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("external_account_id", sa.String(length=255), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=True),
        sa.Column("name", sa.String(length=500), nullable=True),
        sa.Column("seat_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_crm_accounts_company_id", "crm_accounts", ["company_id"])
    op.create_index("ix_crm_accounts_external_account_id", "crm_accounts", ["external_account_id"])

    op.create_table(
        "crm_contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("external_contract_id", sa.String(length=255), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_accounts.id"), nullable=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=True),
        sa.Column("contract_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("price_increase_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expected_renewal_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("seat_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_crm_contracts_company_id", "crm_contracts", ["company_id"])
    op.create_index("ix_crm_contracts_external_contract_id", "crm_contracts", ["external_contract_id"])


def downgrade() -> None:
    op.drop_index("ix_crm_contracts_external_contract_id", table_name="crm_contracts")
    op.drop_index("ix_crm_contracts_company_id", table_name="crm_contracts")
    op.drop_table("crm_contracts")
    op.drop_index("ix_crm_accounts_external_account_id", table_name="crm_accounts")
    op.drop_index("ix_crm_accounts_company_id", table_name="crm_accounts")
    op.drop_table("crm_accounts")

    op.drop_column("invoice_line_items", "is_manual_override")
    op.drop_column("invoice_line_items", "external_line_item_id")
    op.drop_column("invoices", "credit_amount")
    op.drop_column("invoices", "external_invoice_id")
    op.drop_column("audits", "scan_error")
    op.drop_column("audits", "scan_report")
