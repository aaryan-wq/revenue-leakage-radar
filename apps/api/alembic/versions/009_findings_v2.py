"""Finding schema v2

Revision ID: 009
Revises: 008
Create Date: 2026-06-30
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("findings", sa.Column("rule_name", sa.String(length=200), nullable=True))
    op.add_column("findings", sa.Column("status", sa.String(length=32), nullable=False, server_default="open"))
    op.add_column("findings", sa.Column("product_id", sa.String(length=128), nullable=True))
    op.add_column("findings", sa.Column("expected_value", sa.Numeric(18, 4), nullable=True))
    op.add_column("findings", sa.Column("actual_value", sa.Numeric(18, 4), nullable=True))
    op.add_column("findings", sa.Column("difference", sa.Numeric(18, 4), nullable=True))
    op.add_column("findings", sa.Column("calculation_trace", sa.Text(), nullable=True))
    op.add_column("findings", sa.Column("finding_ref", sa.String(length=64), nullable=True))
    op.add_column("findings", sa.Column("rule_version", sa.String(length=32), nullable=True))
    op.create_index("ix_findings_finding_ref", "findings", ["finding_ref"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_findings_finding_ref", table_name="findings")
    op.drop_column("findings", "rule_version")
    op.drop_column("findings", "finding_ref")
    op.drop_column("findings", "calculation_trace")
    op.drop_column("findings", "difference")
    op.drop_column("findings", "actual_value")
    op.drop_column("findings", "expected_value")
    op.drop_column("findings", "product_id")
    op.drop_column("findings", "status")
    op.drop_column("findings", "rule_name")
