"""Add unique constraint on Stripe checkout session IDs to prevent double fulfillment."""

from typing import Sequence, Union

from alembic import op

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_report_purchases_stripe_checkout_session_id",
        "report_purchases",
        ["stripe_checkout_session_id"],
        unique=True,
        postgresql_where="stripe_checkout_session_id IS NOT NULL",
    )


def downgrade() -> None:
    op.drop_index(
        "uq_report_purchases_stripe_checkout_session_id",
        table_name="report_purchases",
    )
