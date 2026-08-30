"""Estimator database schema."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_token", sa.String(64), nullable=False),
        sa.Column("anonymous_id", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="started"),
        sa.Column("country", sa.String(8), nullable=True),
        sa.Column("industry", sa.String(64), nullable=True),
        sa.Column("company_type", sa.String(32), nullable=True),
        sa.Column("arr_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("arr_currency", sa.String(8), nullable=True),
        sa.Column("customer_count", sa.Integer(), nullable=True),
        sa.Column("subscription_count", sa.Integer(), nullable=True),
        sa.Column("estimator_version", sa.String(32), nullable=False, server_default="1.0.0"),
        sa.Column("questionnaire_version", sa.String(32), nullable=False, server_default="2.0"),
        sa.Column("model_version", sa.String(32), nullable=False, server_default="1.0.0"),
        sa.Column("share_token", sa.String(64), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_assessments_session_token", "assessments", ["session_token"], unique=True)
    op.create_index("ix_assessments_status", "assessments", ["status"])
    op.create_index("ix_assessments_share_token", "assessments", ["share_token"], unique=True)

    op.create_table(
        "assessment_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.String(128), nullable=False),
        sa.Column("section", sa.String(64), nullable=False),
        sa.Column("answer_type", sa.String(32), nullable=False),
        sa.Column("value_numeric", sa.Numeric(18, 4), nullable=True),
        sa.Column("value_boolean", sa.Boolean(), nullable=True),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("value_enum", sa.String(128), nullable=True),
        sa.Column("value_json", postgresql.JSONB(), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("source", sa.String(32), nullable=False, server_default="user"),
    )
    op.create_index("ix_assessment_answers_assessment_id", "assessment_answers", ["assessment_id"])

    op.create_table(
        "assessment_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "estimator_model_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("version", sa.String(32), nullable=False, unique=True),
        sa.Column("questionnaire_version", sa.String(32), nullable=False),
        sa.Column("reason_for_change", sa.Text(), nullable=True),
        sa.Column("prior_version", sa.String(32), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="production"),
        sa.Column("deployed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "assessment_hypotheses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hypothesis_id", sa.String(8), nullable=False),
        sa.Column("prior_probability", sa.Numeric(8, 6), nullable=True),
        sa.Column("posterior_probability", sa.Numeric(8, 6), nullable=True),
        sa.Column("exposure_base", sa.Numeric(18, 2), nullable=True),
        sa.Column("affected_rate", sa.Numeric(8, 6), nullable=True),
        sa.Column("severity", sa.Numeric(8, 6), nullable=True),
        sa.Column("persistence", sa.Numeric(8, 4), nullable=True),
        sa.Column("recoverability", sa.Numeric(8, 6), nullable=True),
        sa.Column("detectability", sa.Numeric(8, 6), nullable=True),
        sa.Column("raw_opportunity_low", sa.Numeric(18, 2), nullable=True),
        sa.Column("raw_opportunity_mid", sa.Numeric(18, 2), nullable=True),
        sa.Column("raw_opportunity_high", sa.Numeric(18, 2), nullable=True),
        sa.Column("correlation_adjustment", sa.Numeric(18, 2), nullable=True),
        sa.Column("final_low", sa.Numeric(18, 2), nullable=True),
        sa.Column("final_mid", sa.Numeric(18, 2), nullable=True),
        sa.Column("final_high", sa.Numeric(18, 2), nullable=True),
        sa.Column("model_version", sa.String(32), nullable=False),
    )

    op.create_table(
        "assessment_model_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_version", sa.String(32), nullable=False),
        sa.Column("random_seed", sa.Integer(), nullable=False),
        sa.Column("simulation_count", sa.Integer(), nullable=False),
        sa.Column("p10", sa.Numeric(18, 2), nullable=True),
        sa.Column("p25", sa.Numeric(18, 2), nullable=True),
        sa.Column("p50", sa.Numeric(18, 2), nullable=True),
        sa.Column("p75", sa.Numeric(18, 2), nullable=True),
        sa.Column("p90", sa.Numeric(18, 2), nullable=True),
        sa.Column("detectable_p25", sa.Numeric(18, 2), nullable=True),
        sa.Column("detectable_p75", sa.Numeric(18, 2), nullable=True),
        sa.Column("central_estimate", sa.Numeric(18, 2), nullable=True),
        sa.Column("confidence_score", sa.String(32), nullable=True),
        sa.Column("complexity_score", sa.Integer(), nullable=True),
        sa.Column("scenario", sa.String(32), nullable=False, server_default="central"),
        sa.Column("runtime_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "assessment_assumptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assumption_id", sa.String(128), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("unit", sa.String(32), nullable=True),
        sa.Column("source", sa.String(32), nullable=False, server_default="model_prior"),
        sa.Column("assumption_type", sa.String(32), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("confidence", sa.String(32), nullable=False, server_default="low"),
    )

    op.create_table(
        "assessment_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("model_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("result_json", postgresql.JSONB(), nullable=False),
        sa.Column("narrative_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "estimator_lead_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(128), nullable=True),
        sa.Column("lead_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("scan_intent", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "estimator_calibration_observations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("audits.id", ondelete="SET NULL"), nullable=True),
        sa.Column("predicted_low", sa.Numeric(18, 2), nullable=True),
        sa.Column("predicted_mid", sa.Numeric(18, 2), nullable=True),
        sa.Column("predicted_high", sa.Numeric(18, 2), nullable=True),
        sa.Column("actual_leakage", sa.Numeric(18, 2), nullable=True),
        sa.Column("absolute_error", sa.Numeric(18, 2), nullable=True),
        sa.Column("relative_error", sa.Numeric(8, 4), nullable=True),
        sa.Column("in_interval", sa.Boolean(), nullable=True),
        sa.Column("model_version", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("estimator_calibration_observations")
    op.drop_table("estimator_lead_profiles")
    op.drop_table("assessment_results")
    op.drop_table("assessment_assumptions")
    op.drop_table("assessment_model_runs")
    op.drop_table("assessment_hypotheses")
    op.drop_table("estimator_model_versions")
    op.drop_table("assessment_events")
    op.drop_table("assessment_answers")
    op.drop_index("ix_assessments_share_token", table_name="assessments")
    op.drop_index("ix_assessments_status", table_name="assessments")
    op.drop_index("ix_assessments_session_token", table_name="assessments")
    op.drop_table("assessments")
