"""Link audits to optional estimator assessments for handoff context."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "audits",
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_audits_assessment_id",
        "audits",
        "assessments",
        ["assessment_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_audits_assessment_id", "audits", ["assessment_id"])


def downgrade() -> None:
    op.drop_index("ix_audits_assessment_id", table_name="audits")
    op.drop_constraint("fk_audits_assessment_id", "audits", type_="foreignkey")
    op.drop_column("audits", "assessment_id")
