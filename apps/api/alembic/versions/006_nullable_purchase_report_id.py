"""Nullable report_id on report_purchases

Revision ID: 006
Revises: 005
Create Date: 2025-06-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "report_purchases",
        "report_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "report_purchases",
        "report_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
