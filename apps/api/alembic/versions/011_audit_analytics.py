"""Audit analytics summary fields

Revision ID: 011
Revises: 010
Create Date: 2026-07-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("audits", sa.Column("audit_type", sa.String(length=32), nullable=False, server_default="free"))
    op.add_column("audits", sa.Column("is_anonymous", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("audits", sa.Column("billing_platform_detected", sa.String(length=50), nullable=True))
    op.add_column("audits", sa.Column("crm_platform_detected", sa.String(length=50), nullable=True))
    op.add_column("audits", sa.Column("csv_file_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("audits", sa.Column("billing_file_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("audits", sa.Column("crm_file_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("audits", sa.Column("upload_completed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("audits", sa.Column("verification_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("audits", sa.Column("verification_completed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("audits", sa.Column("verification_duration_ms", sa.Integer(), nullable=True))
    op.add_column("audits", sa.Column("rules_total", sa.Integer(), nullable=True))
    op.add_column("audits", sa.Column("rules_executed", sa.Integer(), nullable=True))
    op.add_column("audits", sa.Column("rules_skipped", sa.Integer(), nullable=True))
    op.add_column("audits", sa.Column("rules_failed", sa.Integer(), nullable=True))
    op.add_column("audits", sa.Column("findings_total", sa.Integer(), nullable=True))
    op.add_column("audits", sa.Column("estimated_monthly_leakage", sa.Numeric(18, 4), nullable=True))
    op.add_column("audits", sa.Column("estimated_annual_leakage", sa.Numeric(18, 4), nullable=True))
    op.add_column("audits", sa.Column("coverage_score", sa.Numeric(5, 2), nullable=True))
    op.add_column("audits", sa.Column("confidence_score", sa.Numeric(5, 2), nullable=True))
    op.add_column("audits", sa.Column("top_rule_category", sa.String(length=64), nullable=True))
    op.add_column("audits", sa.Column("report_unlocked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("audits", sa.Column("checkout_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("audits", sa.Column("checkout_completed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "audits",
        sa.Column("enterprise_interest_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "audits",
        sa.Column("billing_data_present", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "audits",
        sa.Column("crm_data_present", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "audits",
        sa.Column("invoice_data_present", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "audits",
        sa.Column("subscription_data_present", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "audits",
        sa.Column("line_item_data_present", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "audits",
        sa.Column("price_data_present", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "audits",
        sa.Column("coupon_data_present", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "audits",
        sa.Column("credit_data_present", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_index("ix_audits_audit_type", "audits", ["audit_type"], unique=False)
    op.create_index("ix_audits_checkout_completed_at", "audits", ["checkout_completed_at"], unique=False)
    op.create_index("ix_audits_verification_completed_at", "audits", ["verification_completed_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audits_verification_completed_at", table_name="audits")
    op.drop_index("ix_audits_checkout_completed_at", table_name="audits")
    op.drop_index("ix_audits_audit_type", table_name="audits")

    for column in (
        "credit_data_present",
        "coupon_data_present",
        "price_data_present",
        "line_item_data_present",
        "subscription_data_present",
        "invoice_data_present",
        "crm_data_present",
        "billing_data_present",
        "enterprise_interest_flag",
        "checkout_completed_at",
        "checkout_started_at",
        "report_unlocked_at",
        "top_rule_category",
        "confidence_score",
        "coverage_score",
        "estimated_annual_leakage",
        "estimated_monthly_leakage",
        "findings_total",
        "rules_failed",
        "rules_skipped",
        "rules_executed",
        "rules_total",
        "verification_duration_ms",
        "verification_completed_at",
        "verification_started_at",
        "upload_completed_at",
        "crm_file_count",
        "billing_file_count",
        "csv_file_count",
        "crm_platform_detected",
        "billing_platform_detected",
        "is_anonymous",
        "audit_type",
    ):
        op.drop_column("audits", column)
