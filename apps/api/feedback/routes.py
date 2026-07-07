import logging
from datetime import UTC, datetime
from enum import Enum

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from core.config import settings
from notifications.templates import feedback_email

logger = logging.getLogger(__name__)

router = APIRouter(tags=["feedback"])


class FeedbackCategory(str, Enum):
    GENERAL = "general"
    BUG = "bug"
    FEATURE = "feature"
    BILLING = "billing"
    OTHER = "other"


class FeedbackRequest(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    email: str = Field(min_length=3, max_length=320)
    message: str = Field(min_length=10, max_length=5000)
    category: FeedbackCategory = FeedbackCategory.GENERAL
    page_url: str | None = Field(default=None, max_length=2000)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip()
        if "@" not in normalized or "." not in normalized.split("@")[-1]:
            raise ValueError("Invalid email address")
        return normalized


class FeedbackResponse(BaseModel):
    ok: bool = True


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(body: FeedbackRequest) -> FeedbackResponse:
    if not settings.resend_api_key:
        logger.warning("Feedback submission rejected: Resend not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feedback delivery is temporarily unavailable. Please email us directly.",
        )

    sent = feedback_email(
        to=settings.feedback_email,
        sender_name=body.name,
        sender_email=str(body.email),
        category=body.category.value,
        message=body.message,
        page_url=body.page_url,
        submitted_at=datetime.now(UTC),
    )
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="We could not deliver your feedback. Please email us directly.",
        )

    return FeedbackResponse()
