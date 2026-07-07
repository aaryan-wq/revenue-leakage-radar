from datetime import datetime
from html import escape

from core.config import settings
from notifications.client import send_email


def purchase_confirmation_email(*, to: str, report_url: str) -> bool:
    subject = "Your Paevo report purchase is confirmed"
    text = (
        "Thank you for purchasing your Revenue Verification Report on Paevo.\n\n"
        f"View your report: {report_url}\n\n"
        f"Questions? Contact us at {settings.support_email}."
    )
    html = (
        "<p>Thank you for purchasing your <strong>Revenue Verification Report</strong> on Paevo.</p>"
        f'<p><a href="{report_url}">View your report</a></p>'
        f"<p>Questions? Contact us at {settings.support_email}.</p>"
    )
    return send_email(to=to, subject=subject, html=html, text=text)


def report_ready_email(*, to: str, summary_url: str) -> bool:
    subject = "Your Paevo audit is ready"
    text = (
        "Your revenue audit scan has completed.\n\n"
        f"View your free summary: {summary_url}\n\n"
        f"Questions? Contact us at {settings.support_email}."
    )
    html = (
        "<p>Your revenue audit scan has completed.</p>"
        f'<p><a href="{summary_url}">View your free summary</a></p>'
        f"<p>Questions? Contact us at {settings.support_email}.</p>"
    )
    return send_email(to=to, subject=subject, html=html, text=text)


def feedback_email(
    *,
    to: str,
    sender_name: str | None,
    sender_email: str,
    category: str,
    message: str,
    page_url: str | None,
    submitted_at: datetime,
) -> bool:
    display_name = sender_name.strip() if sender_name and sender_name.strip() else "Anonymous"
    subject = f"[Paevo Feedback] {category} — from {sender_email}"
    timestamp = submitted_at.strftime("%Y-%m-%d %H:%M UTC")
    safe_message = escape(message)
    safe_page_url = escape(page_url) if page_url else None
    safe_name = escape(display_name)
    safe_email = escape(sender_email)
    safe_category = escape(category)
    page_line = f"\nPage: {page_url}" if page_url else ""
    text = (
        f"New feedback from {display_name} ({sender_email})\n"
        f"Category: {category}\n"
        f"Submitted: {timestamp}{page_line}\n\n"
        f"{message}"
    )
    page_html = f"<p><strong>Page:</strong> {safe_page_url}</p>" if safe_page_url else ""
    html = (
        f"<p><strong>From:</strong> {safe_name} ({safe_email})</p>"
        f"<p><strong>Category:</strong> {safe_category}</p>"
        f"<p><strong>Submitted:</strong> {timestamp}</p>"
        f"{page_html}"
        f"<hr />"
        f"<pre style=\"white-space:pre-wrap;font-family:inherit\">{safe_message}</pre>"
    )
    return send_email(to=to, subject=subject, html=html, text=text)
