import secrets
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from estimator.config import MODEL_VERSION, QUESTIONNAIRE_VERSION
from estimator.modeling.fingerprint import is_stale_result
from estimator.modeling.pipeline import run_model
from estimator.questionnaire.engine import (
    answered_question_ids,
    answers_to_map,
    completion_progress,
    current_section,
    next_unanswered_question,
    pending_question_ids,
    visible_question_ids,
)
from estimator.questionnaire.schema import get_question_by_id
from estimator.validation.checks import check_contradictions, check_sanity
from models.estimator import (
    Assessment,
    AssessmentAnswer,
    AssessmentAssumption,
    AssessmentEvent,
    AssessmentHypothesis,
    AssessmentModelRun,
    AssessmentResult,
    CalibrationObservation,
    LeadProfile,
)


def create_assessment(db: Session, anonymous_id: str | None = None) -> Assessment:
    assessment = Assessment(
        session_token=secrets.token_urlsafe(32),
        anonymous_id=anonymous_id,
        status="started",
        estimator_version="1.0.0",
        questionnaire_version=QUESTIONNAIRE_VERSION,
        model_version=MODEL_VERSION,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    record_event(db, assessment.id, "estimator_started")
    return assessment


def get_assessment(db: Session, assessment_id: uuid.UUID) -> Assessment | None:
    return db.query(Assessment).filter(Assessment.id == assessment_id).first()


def get_assessment_by_token(db: Session, token: str) -> Assessment | None:
    return db.query(Assessment).filter(Assessment.session_token == token).first()


def get_assessment_by_share_token(db: Session, token: str) -> Assessment | None:
    return db.query(Assessment).filter(Assessment.share_token == token).first()


def _answers_dict(assessment: Assessment) -> dict[str, Any]:
    rows = [
        {
            "question_id": a.question_id,
            "value_numeric": a.value_numeric,
            "value_boolean": a.value_boolean,
            "value_text": a.value_text,
            "value_enum": a.value_enum,
            "value_json": a.value_json,
        }
        for a in assessment.answers
    ]
    return answers_to_map(rows)


def upsert_answer(db: Session, assessment: Assessment, payload: dict[str, Any]) -> AssessmentAnswer:
    question = get_question_by_id(payload["question_id"], assessment.questionnaire_version)
    if question is None:
        raise ValueError("Unknown question")

    existing = (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.assessment_id == assessment.id,
            AssessmentAnswer.question_id == payload["question_id"],
        )
        .first()
    )
    if existing is None:
        existing = AssessmentAnswer(
            assessment_id=assessment.id,
            question_id=payload["question_id"],
            section=question["section"],
            answer_type=question["type"],
        )
        db.add(existing)

    existing.value_numeric = payload.get("value_numeric")
    existing.value_boolean = payload.get("value_boolean")
    existing.value_text = payload.get("value_text")
    existing.value_enum = payload.get("value_enum")
    existing.value_json = payload.get("value_json")

    if payload["question_id"] == "profile.arr_amount" and payload.get("value_numeric") is not None:
        assessment.arr_amount = Decimal(str(payload["value_numeric"]))
        if payload.get("value_text"):
            assessment.arr_currency = payload["value_text"]
    if payload["question_id"] == "profile.customer_count" and payload.get("value_numeric") is not None:
        assessment.customer_count = int(payload["value_numeric"])
    if payload["question_id"] == "profile.company_type":
        assessment.company_type = payload.get("value_enum")

    db.commit()
    db.refresh(existing)
    record_event(db, assessment.id, "question_answered", {"question_id": payload["question_id"]})
    return existing


def _resume_state(assessment: Assessment, answers: dict[str, Any]) -> dict[str, Any]:
    version = assessment.questionnaire_version
    effective_version = QUESTIONNAIRE_VERSION if assessment.status == "completed" else version
    pending = pending_question_ids(answers, effective_version)
    answered = answered_question_ids(answers, effective_version)
    requires_reanswer = assessment.status == "completed" and len(pending) > 0
    return {
        "pending_question_ids": pending,
        "pending_count": len(pending),
        "answered_count": len(answered),
        "has_pending_questions": len(pending) > 0,
        "requires_reanswer": requires_reanswer,
        "is_resuming": len(answered) > 0 and len(pending) > 0,
        "questionnaire_version": version,
        "current_questionnaire_version": QUESTIONNAIRE_VERSION,
    }


def assessment_state(assessment: Assessment) -> dict[str, Any]:
    answers = _answers_dict(assessment)
    progress = completion_progress(answers, assessment.questionnaire_version)
    next_q = next_unanswered_question(answers, assessment.questionnaire_version)
    return {
        "assessment_id": str(assessment.id),
        "status": assessment.status,
        "answers": answers,
        "progress": progress,
        "current_section": current_section(answers, assessment.questionnaire_version),
        "next_question": next_q,
        "visible_question_ids": visible_question_ids(answers, assessment.questionnaire_version),
        "resume": _resume_state(assessment, answers),
    }


def validate_assessment(assessment: Assessment) -> dict[str, Any]:
    answers = _answers_dict(assessment)
    return {
        "warnings": check_sanity(answers),
        "contradictions": check_contradictions(answers),
    }


def calculate_assessment(
    db: Session,
    assessment: Assessment,
    *,
    random_seed: int = 42,
    scenario: str = "central",
) -> dict[str, Any]:
    answers = _answers_dict(assessment)
    progress = completion_progress(answers, assessment.questionnaire_version)
    result = run_model(
        answers,
        random_seed=random_seed,
        scenario=scenario,
        completion_rate=progress["completion_rate"],
    )

    model_run = AssessmentModelRun(
        assessment_id=assessment.id,
        model_version=result["model_version"],
        random_seed=random_seed,
        simulation_count=result["simulation_count"],
        p10=Decimal(str(result["percentiles"]["p10"])),
        p25=Decimal(str(result["percentiles"]["p25"])),
        p50=Decimal(str(result["percentiles"]["p50"])),
        p75=Decimal(str(result["percentiles"]["p75"])),
        p90=Decimal(str(result["percentiles"]["p90"])),
        detectable_p25=Decimal(str(result["detectable"]["low"])),
        detectable_p75=Decimal(str(result["detectable"]["high"])),
        central_estimate=Decimal(str(result["estimate"]["central"])),
        confidence_score=result["confidence"],
        complexity_score=result["complexity"]["total"],
        scenario=scenario,
        runtime_ms=result["runtime_ms"],
    )
    db.add(model_run)
    db.flush()

    db.query(AssessmentHypothesis).filter(AssessmentHypothesis.assessment_id == assessment.id).delete()
    for hyp in result["hypothesis_breakdown"]:
        db.add(
            AssessmentHypothesis(
                assessment_id=assessment.id,
                hypothesis_id=hyp["hypothesis_id"],
                posterior_probability=Decimal(str(hyp["posterior_probability"])),
                final_low=Decimal(str(hyp["low"])),
                final_mid=Decimal(str(hyp["mid"])),
                final_high=Decimal(str(hyp["high"])),
                model_version=result["model_version"],
            )
        )

    db.query(AssessmentAssumption).filter(AssessmentAssumption.assessment_id == assessment.id).delete()
    for assumption in result["assumptions"]:
        db.add(
            AssessmentAssumption(
                assessment_id=assessment.id,
                assumption_id=assumption["assumption_id"],
                category=assumption["category"],
                value=assumption["value"],
                unit=assumption.get("unit"),
                source=assumption["source"],
                assumption_type=assumption["type"],
                version=assumption["version"],
                confidence=assumption["confidence"],
            )
        )

    existing_result = db.query(AssessmentResult).filter(AssessmentResult.assessment_id == assessment.id).first()
    if existing_result:
        existing_result.model_run_id = model_run.id
        existing_result.result_json = result
    else:
        db.add(
            AssessmentResult(
                assessment_id=assessment.id,
                model_run_id=model_run.id,
                result_json=result,
            )
        )

    assessment.status = "completed"
    assessment.completed_at = datetime.now(timezone.utc)
    db.commit()
    record_event(db, assessment.id, "estimator_completed", {"scenario": scenario})
    result["model_run_id"] = str(model_run.id)
    return result


def get_result(
    db: Session,
    assessment: Assessment,
    *,
    refresh_if_stale: bool = True,
) -> dict[str, Any] | None:
    row = db.query(AssessmentResult).filter(AssessmentResult.assessment_id == assessment.id).first()
    if row is None:
        return None

    payload = dict(row.result_json)
    narrative = row.narrative_json

    if refresh_if_stale and is_stale_result(payload):
        scenario = str(payload.get("scenario") or "central")
        random_seed = int(payload.get("random_seed") or 42)
        payload = calculate_assessment(
            db,
            assessment,
            random_seed=random_seed,
            scenario=scenario,
        )
        row = db.query(AssessmentResult).filter(AssessmentResult.assessment_id == assessment.id).first()
        narrative = row.narrative_json if row else narrative

    if narrative:
        payload["narrative"] = narrative
    return payload


def save_lead(
    db: Session,
    assessment: Assessment,
    email: str,
    company_name: str | None,
    role: str | None,
) -> LeadProfile:
    result = get_result(db, assessment)
    score = compute_lead_score(assessment, result)
    existing = db.query(LeadProfile).filter(LeadProfile.assessment_id == assessment.id).first()
    if existing is None:
        existing = LeadProfile(assessment_id=assessment.id)
        db.add(existing)
    existing.email = email
    existing.company_name = company_name
    existing.role = role
    existing.lead_score = score
    db.commit()
    db.refresh(existing)
    record_event(db, assessment.id, "assessment_email_saved")
    return existing


def compute_lead_score(assessment: Assessment, result: dict[str, Any] | None) -> int:
    score = 0
    if assessment.arr_amount and float(assessment.arr_amount) >= 5_000_000:
        score += 10
    if assessment.arr_amount and float(assessment.arr_amount) >= 10_000_000:
        score += 10
    if result:
        if result.get("complexity", {}).get("total", 0) > 25:
            score += 15
        central = result.get("estimate", {}).get("central", 0)
        if central > 50_000:
            score += 15
        if central > 100_000:
            score += 15
    return min(score, 100)


def create_share_token(db: Session, assessment: Assessment) -> str:
    if not assessment.share_token:
        assessment.share_token = secrets.token_urlsafe(24)
        db.commit()
    record_event(db, assessment.id, "result_shared")
    return assessment.share_token


def record_event(
    db: Session,
    assessment_id: uuid.UUID,
    event_type: str,
    payload: dict[str, Any] | None = None,
) -> None:
    db.add(AssessmentEvent(assessment_id=assessment_id, event_type=event_type, payload=payload))
    db.commit()


def record_calibration(
    db: Session,
    assessment_id: uuid.UUID | None,
    audit_id: uuid.UUID | None,
    predicted: dict[str, float],
    actual_leakage: float,
    model_version: str,
) -> CalibrationObservation:
    low = predicted.get("low", 0)
    high = predicted.get("high", 0)
    mid = predicted.get("central", 0)
    in_interval = low <= actual_leakage <= high if high else None
    obs = CalibrationObservation(
        assessment_id=assessment_id,
        audit_id=audit_id,
        predicted_low=Decimal(str(low)),
        predicted_mid=Decimal(str(mid)),
        predicted_high=Decimal(str(high)),
        actual_leakage=Decimal(str(actual_leakage)),
        absolute_error=Decimal(str(abs(actual_leakage - mid))),
        relative_error=Decimal(str(abs(actual_leakage - mid) / max(actual_leakage, 1))),
        in_interval=in_interval,
        model_version=model_version,
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs
