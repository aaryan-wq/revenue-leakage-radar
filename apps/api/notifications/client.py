import logging

from core.config import settings

logger = logging.getLogger(__name__)


def send_email(*, to: str, subject: str, html: str, text: str) -> bool:
    if not settings.resend_api_key:
        logger.info("Resend not configured; skipping email to %s (%s)", to, subject)
        return False

    try:
        import resend

        resend.api_key = settings.resend_api_key
        resend.Emails.send(
            {
                "from": settings.from_email,
                "to": [to],
                "subject": subject,
                "html": html,
                "text": text,
            }
        )
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to)
        return False
