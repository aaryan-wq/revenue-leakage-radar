"""Ingestion metadata on audits

Revision ID: 002
Revises: 001
Create Date: 2025-06-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("audits", sa.Column("platform", sa.String(length=50), nullable=True))
    op.add_column("audits", sa.Column("column_mappings", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("audits", sa.Column("validation_report", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("audits", sa.Column("validation_result", sa.String(length=50), nullable=True))
    op.add_column("audits", sa.Column("ingestion_error", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("audits", "ingestion_error")
    op.drop_column("audits", "validation_result")
    op.drop_column("audits", "validation_report")
    op.drop_column("audits", "column_mappings")
    op.drop_column("audits", "platform")
