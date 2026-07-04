"""Line items: unresolved invoice reference

Revision ID: 010
Revises: 009
Create Date: 2026-06-30
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "invoice_line_items",
        sa.Column("referenced_invoice_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        "ix_invoice_line_items_referenced_invoice_id",
        "invoice_line_items",
        ["referenced_invoice_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_invoice_line_items_referenced_invoice_id", table_name="invoice_line_items")
    op.drop_column("invoice_line_items", "referenced_invoice_id")
