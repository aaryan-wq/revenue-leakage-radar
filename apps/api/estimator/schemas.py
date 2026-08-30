from typing import Any

from pydantic import BaseModel, Field


class CreateAssessmentRequest(BaseModel):
    anonymous_id: str | None = None


class AnswerPayload(BaseModel):
    question_id: str
    value_numeric: float | None = None
    value_boolean: bool | None = None
    value_text: str | None = None
    value_enum: str | None = None
    value_json: list[str] | dict[str, Any] | None = None


class PatchAnswersRequest(BaseModel):
    answers: list[AnswerPayload]


class CalculateRequest(BaseModel):
    random_seed: int | None = 42
    scenario: str = Field(default="aggressive", pattern="^(conservative|central|aggressive)$")


class LeadRequest(BaseModel):
    email: str
    company_name: str | None = None
    role: str | None = None
    scan_intent: bool = False


class NarrativeRequest(BaseModel):
    view: str = Field(default="executive", pattern="^(executive|finance|technical)$")
