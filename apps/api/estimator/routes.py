import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from estimator import service
from estimator.modeling.complexity import compute_complexity
from estimator.modeling.normalize import normalize_answers
from estimator.narrative.service import fallback_narrative, generate_narrative
from estimator.questionnaire.engine import answers_to_map, completion_progress
from estimator.questionnaire.schema import load_questionnaire
from estimator.schemas import (
    CalculateRequest,
    CreateAssessmentRequest,
    LeadRequest,
    NarrativeRequest,
    PatchAnswersRequest,
)
from estimator.service import _answers_dict
from models.estimator import Assessment, AssessmentResult

router = APIRouter(prefix="/estimator", tags=["estimator"])


def _get_assessment_or_404(db: Session, assessment_id: uuid.UUID) -> Assessment:
    row = service.get_assessment(db, assessment_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return row


@router.post("/assessments")
def create_assessment(body: CreateAssessmentRequest, db: Session = Depends(get_db)):
    assessment = service.create_assessment(db, anonymous_id=body.anonymous_id)
    return {
        "assessment_id": str(assessment.id),
        "session_token": assessment.session_token,
        "questionnaire_version": assessment.questionnaire_version,
    }


@router.get("/assessments/{assessment_id}")
def get_assessment(assessment_id: uuid.UUID, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    state = service.assessment_state(assessment)
    answers = _answers_dict(assessment)
    normalized = normalize_answers(answers) if answers else {}
    complexity = compute_complexity(normalized) if normalized.get("arr_usd") else None
    return {**state, "complexity_preview": complexity}


@router.get("/questionnaire")
def get_questionnaire():
    return load_questionnaire()


@router.patch("/assessments/{assessment_id}/answers")
def patch_answers(
    assessment_id: uuid.UUID,
    body: PatchAnswersRequest,
    db: Session = Depends(get_db),
):
    assessment = _get_assessment_or_404(db, assessment_id)
    for answer in body.answers:
        service.upsert_answer(db, assessment, answer.model_dump(exclude_none=True))
    db.refresh(assessment)
    return service.assessment_state(assessment)


@router.get("/assessments/{assessment_id}/next")
def get_next_question(assessment_id: uuid.UUID, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    state = service.assessment_state(assessment)
    return {
        "next_question": state["next_question"],
        "progress": state["progress"],
        "current_section": state["current_section"],
    }


@router.post("/assessments/{assessment_id}/validate")
def validate_assessment(assessment_id: uuid.UUID, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    return service.validate_assessment(assessment)


@router.post("/assessments/{assessment_id}/calculate")
def calculate_assessment(
    assessment_id: uuid.UUID,
    body: CalculateRequest,
    db: Session = Depends(get_db),
):
    assessment = _get_assessment_or_404(db, assessment_id)
    answers = _answers_dict(assessment)
    progress = completion_progress(answers, assessment.questionnaire_version)
    if not progress["is_complete"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assessment incomplete")

    validation = service.validate_assessment(assessment)
    if validation["contradictions"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Please resolve contradictions", "contradictions": validation["contradictions"]},
        )

    result = service.calculate_assessment(
        db,
        assessment,
        random_seed=body.random_seed or 42,
        scenario=body.scenario,
    )
    try:
        narrative = generate_narrative(result, view="executive")
    except Exception:
        narrative = fallback_narrative(result)

    row = db.query(AssessmentResult).filter(AssessmentResult.assessment_id == assessment.id).first()
    if row:
        row.narrative_json = narrative
        db.commit()

    return {**result, "narrative": narrative}


@router.get("/assessments/{assessment_id}/result")
def get_result(assessment_id: uuid.UUID, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    result = service.get_result(db, assessment, refresh_if_stale=True)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not calculated yet")
    return result


@router.post("/assessments/{assessment_id}/narrative")
def post_narrative(
    assessment_id: uuid.UUID,
    body: NarrativeRequest,
    db: Session = Depends(get_db),
):
    assessment = _get_assessment_or_404(db, assessment_id)
    result = service.get_result(db, assessment, refresh_if_stale=True)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not calculated yet")
    try:
        narrative = generate_narrative(result, view=body.view)
    except Exception:
        narrative = fallback_narrative(result, view=body.view)
    return narrative


@router.post("/assessments/{assessment_id}/lead")
def save_lead(assessment_id: uuid.UUID, body: LeadRequest, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    lead, email_sent = service.save_lead(db, assessment, body.email, body.company_name, body.role)
    if body.scan_intent:
        lead.scan_intent = True
        db.commit()
    return {"lead_id": str(lead.id), "lead_score": lead.lead_score, "email_sent": email_sent}


@router.post("/assessments/{assessment_id}/share")
def create_share(assessment_id: uuid.UUID, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    token = service.create_share_token(db, assessment)
    return {"share_token": token, "share_path": f"/saas-revenue-leakage-calculator/share/{token}"}


@router.get("/share/{token}")
def get_share(token: str, db: Session = Depends(get_db)):
    assessment = service.get_assessment_by_share_token(db, token)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found")
    result = service.get_result(db, assessment, refresh_if_stale=True)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not available")
    return {
        "disclaimer": "Estimate based on answers, not billing records.",
        "arr_usd": result.get("arr_usd"),
        "estimate": result.get("estimate"),
        "benchmark_context": result.get("benchmark_context"),
        "top_hypotheses": result.get("top_hypotheses", [])[:3],
        "confidence": result.get("confidence"),
    }
