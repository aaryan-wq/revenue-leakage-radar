"""Finding attribution schema

Revision ID: 008
Revises: 007
Create Date: 2025-06-30
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "findings",
        sa.Column("leak_family", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "findings",
        sa.Column("attribution", sa.String(length=16), nullable=False, server_default="primary"),
    )
    op.add_column(
        "findings",
        sa.Column("primary_finding_ref", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("findings", "primary_finding_ref")
    op.drop_column("findings", "attribution")
    op.drop_column("findings", "leak_family")
