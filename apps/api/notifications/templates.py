from datetime import datetime
from html import escape

from core.config import settings
from notifications.client import send_email


def _format_usd(value: float) -> str:
    if value >= 1_000_000:
        text = f"${value / 1_000_000:.1f}M"
        return text.replace(".0M", "M")
    if value >= 1_000:
        return f"${value / 1_000:.0f}k"
    return f"${value:,.0f}"


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


def estimator_summary_email(
    *,
    to: str,
    estimate_high: float,
    arr_usd: float | None,
    top_mechanisms: list[dict[str, str | float]],
    result_url: str,
    share_url: str | None,
    scan_url: str,
) -> bool:
    headline = _format_usd(estimate_high)
    subject = f"Your Paevo revenue leakage estimate: ~{headline}/year"

    arr_line = ""
    if arr_usd and arr_usd > 0:
        pct = (estimate_high / arr_usd) * 100
        arr_line = f"About {pct:.1f}% of your {_format_usd(arr_usd)} ARR.\n"

    mechanism_lines: list[str] = []
    for item in top_mechanisms[:3]:
        name = str(item.get("name", "Mechanism"))
        amount = _format_usd(float(item.get("amount", 0)))
        mechanism_lines.append(f"- {name}: ~{amount}/year")

    mechanisms_text = "\n".join(mechanism_lines) if mechanism_lines else "- See your full results online"
    share_text = f"\nShare with your team: {share_url}\n" if share_url else ""

    text = (
        "Your estimated recoverable revenue\n\n"
        f"~{headline}/year\n"
        f"{arr_line}\n"
        "Top likely sources (overlap, not additive):\n"
        f"{mechanisms_text}\n\n"
        f"View full results: {result_url}\n"
        f"{share_text}"
        f"Confirm with a free billing scan: {scan_url}\n\n"
        "This estimate is based on your questionnaire answers, not billing records.\n"
        f"Questions? Contact us at {settings.support_email}."
    )

    safe_headline = escape(headline)
    mechanism_html = "".join(
        f"<li><strong>{escape(str(item.get('name', 'Mechanism')))}</strong>: "
        f"~{escape(_format_usd(float(item.get('amount', 0))))}/year</li>"
        for item in top_mechanisms[:3]
    )
    if not mechanism_html:
        mechanism_html = "<li>See your full results online</li>"

    arr_html = ""
    if arr_usd and arr_usd > 0:
        pct = (estimate_high / arr_usd) * 100
        arr_html = (
            f"<p>About {pct:.1f}% of your {_format_usd(arr_usd)} annual recurring revenue.</p>"
        )

    share_html = (
        f'<p><a href="{escape(share_url)}">Share with your team</a></p>' if share_url else ""
    )

    html = (
        "<p>Your estimated recoverable revenue</p>"
        f"<p style=\"font-size:24px;font-weight:600\">~{safe_headline}/year</p>"
        f"{arr_html}"
        "<p><strong>Top likely sources</strong> (overlap, not additive):</p>"
        f"<ul>{mechanism_html}</ul>"
        f'<p><a href="{escape(result_url)}">View full results</a></p>'
        f"{share_html}"
        f'<p><a href="{escape(scan_url)}">Confirm with a free billing scan</a></p>'
        "<p><em>This estimate is based on your questionnaire answers, not billing records.</em></p>"
        f"<p>Questions? Contact us at {escape(settings.support_email)}.</p>"
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
    subject = f"[Paevo Feedback] {category} from {sender_email}"
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
