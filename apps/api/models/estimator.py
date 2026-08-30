"""Estimator schema: assessments, model runs, leads, calibration."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    anonymous_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="started", index=True)
    country: Mapped[str | None] = mapped_column(String(8), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(64), nullable=True)
    company_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    arr_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    arr_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    customer_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subscription_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimator_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")
    questionnaire_version: Mapped[str] = mapped_column(String(32), nullable=False, default="2.0")
    model_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")
    share_token: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    answers: Mapped[list["AssessmentAnswer"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
    events: Mapped[list["AssessmentEvent"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
    hypotheses: Mapped[list["AssessmentHypothesis"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
    model_runs: Mapped[list["AssessmentModelRun"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
    assumptions: Mapped[list["AssessmentAssumption"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
    result: Mapped["AssessmentResult | None"] = relationship(
        back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )
    lead_profile: Mapped["LeadProfile | None"] = relationship(
        back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[str] = mapped_column(String(128), nullable=False)
    section: Mapped[str] = mapped_column(String(64), nullable=False)
    answer_type: Mapped[str] = mapped_column(String(32), nullable=False)
    value_numeric: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    value_boolean: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_enum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    value_json: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="user")

    assessment: Mapped["Assessment"] = relationship(back_populates="answers")


class AssessmentEvent(Base):
    __tablename__ = "assessment_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    assessment: Mapped["Assessment"] = relationship(back_populates="events")


class ModelVersion(Base):
    __tablename__ = "estimator_model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    questionnaire_version: Mapped[str] = mapped_column(String(32), nullable=False)
    reason_for_change: Mapped[str | None] = mapped_column(Text, nullable=True)
    prior_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="production")
    deployed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AssessmentHypothesis(Base):
    __tablename__ = "assessment_hypotheses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hypothesis_id: Mapped[str] = mapped_column(String(8), nullable=False)
    prior_probability: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    posterior_probability: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    exposure_base: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    affected_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    severity: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    persistence: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    recoverability: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    detectability: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    raw_opportunity_low: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    raw_opportunity_mid: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    raw_opportunity_high: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    correlation_adjustment: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    final_low: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    final_mid: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    final_high: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)

    assessment: Mapped["Assessment"] = relationship(back_populates="hypotheses")


class AssessmentModelRun(Base):
    __tablename__ = "assessment_model_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    random_seed: Mapped[int] = mapped_column(Integer, nullable=False)
    simulation_count: Mapped[int] = mapped_column(Integer, nullable=False)
    p10: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    p25: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    p50: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    p75: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    p90: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    detectable_p25: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    detectable_p75: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    central_estimate: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    confidence_score: Mapped[str | None] = mapped_column(String(32), nullable=True)
    complexity_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scenario: Mapped[str] = mapped_column(String(32), nullable=False, default="central")
    runtime_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    assessment: Mapped["Assessment"] = relationship(back_populates="model_runs")


class AssessmentAssumption(Base):
    __tablename__ = "assessment_assumptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assumption_id: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="model_prior")
    assumption_type: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[str] = mapped_column(String(32), nullable=False, default="low")

    assessment: Mapped["Assessment"] = relationship(back_populates="assumptions")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    model_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    result_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    narrative_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    assessment: Mapped["Assessment"] = relationship(back_populates="result")


class LeadProfile(Base):
    __tablename__ = "estimator_lead_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lead_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    scan_intent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    assessment: Mapped["Assessment"] = relationship(back_populates="lead_profile")


class CalibrationObservation(Base):
    __tablename__ = "estimator_calibration_observations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audits.id", ondelete="SET NULL"), nullable=True, index=True
    )
    predicted_low: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    predicted_mid: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    predicted_high: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    actual_leakage: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    absolute_error: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    relative_error: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    in_interval: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
