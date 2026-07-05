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
