import io
import xml.sax.saxutils as saxutils
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from verification.formatting import format_decimal_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from models import Report
from reports.generator import build_report_detail
from verification.recoverable import recoverable_amount_from_payload

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LOGO_CANDIDATES = (
    _REPO_ROOT / "apps" / "api" / "assets" / "logo-full.png",
    _REPO_ROOT / "apps" / "web" / "public" / "brand" / "logo-full.png",
    _REPO_ROOT / "assets" / "logofull.png",
)

# Design-system palette (docs/design-system.md)
SLATE_900 = colors.HexColor("#0F172A")
SLATE_700 = colors.HexColor("#334155")
SLATE_500 = colors.HexColor("#64748B")
SLATE_200 = colors.HexColor("#E2E8F0")
SLATE_100 = colors.HexColor("#F1F5F9")
SLATE_50 = colors.HexColor("#F8FAFC")
ACCENT_BLUE = colors.HexColor("#2563EB")
SEVERITY_HIGH = colors.HexColor("#DC2626")
SEVERITY_MEDIUM = colors.HexColor("#D97706")
SEVERITY_LOW = colors.HexColor("#64748B")

LEFT_MARGIN = 0.75 * inch
RIGHT_MARGIN = 0.75 * inch
TOP_MARGIN = 0.85 * inch
BOTTOM_MARGIN = 0.65 * inch
CONTENT_WIDTH = letter[0] - LEFT_MARGIN - RIGHT_MARGIN

INDEX_ANCHOR = "findings_index"
STATUS_LABELS = {
    "passed": "Passed",
    "issues_found": "Issues found",
    "partial": "Partial coverage",
    "not_run": "Not run",
    "error": "Error",
}


def _hex(color: colors.Color) -> str:
    return f"#{color.hexval()[2:]}"


def _safe(value: Any) -> str:
    return saxutils.escape(str(value if value is not None else ""))


def _col_widths(*ratios: float) -> list[float]:
    total = sum(ratios)
    return [CONTENT_WIDTH * ratio / total for ratio in ratios]


def _format_currency(value: str | float | int | None) -> str:
    if value is None:
        return "-"
    try:
        amount = float(value)
        return f"${amount:,.0f}"
    except (TypeError, ValueError):
        return f"${value}"


def _format_date(iso_value: str | None) -> str:
    if not iso_value:
        return "Current period"
    try:
        parsed = datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
        return parsed.strftime("%b %Y")
    except ValueError:
        return iso_value


def _severity_color(severity: str) -> colors.Color:
    normalized = severity.lower()
    if normalized == "high":
        return SEVERITY_HIGH
    if normalized == "medium":
        return SEVERITY_MEDIUM
    return SEVERITY_LOW


def _finding_anchor(finding_id: str) -> str:
    return f"finding_{finding_id.replace('-', '')}"


def _logo_path() -> Path | None:
    for candidate in _LOGO_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def _recoverable_amount(finding: dict[str, Any]) -> float:
    if finding.get("recoverable_amount") is not None:
        return float(finding["recoverable_amount"])
    return float(recoverable_amount_from_payload(finding))


def _primary_recoverable_amount(finding: dict[str, Any]) -> float:
    if finding.get("attribution") == "secondary":
        return 0.0
    return _recoverable_amount(finding)


def _prepare_findings_for_report(
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    ordered = sorted(findings, key=_recoverable_amount, reverse=True)
    prepared: list[dict[str, Any]] = []
    for index, finding in enumerate(ordered, start=1):
        prepared.append({**finding, "report_index": index})
    return prepared


def _group_findings_by_category(
    findings: list[dict[str, Any]],
) -> list[tuple[str, list[dict[str, Any]]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in findings:
        label = finding.get("category_label") or finding.get("category") or "Other"
        grouped[label].append(finding)

    sections: list[tuple[str, list[dict[str, Any]], float]] = []
    for label, items in grouped.items():
        sorted_items = sorted(items, key=lambda row: row.get("report_index", 0))
        category_arr = sum(_primary_recoverable_amount(row) for row in sorted_items)
        sections.append((label, sorted_items, category_arr))

    sections.sort(key=lambda row: row[2], reverse=True)
    return [(label, items) for label, items, _ in sections]


def _finding_metrics_table(finding: dict[str, Any]) -> tuple[list[str], list[str]]:
    semantics = finding.get("leakage_semantics")
    recoverable = _format_currency(finding.get("recoverable_amount") or _recoverable_amount(finding))
    confidence = f"{finding['confidence']}%"

    if finding.get("attribution") == "secondary":
        return (
            ["Excluded ARR", "Headline impact", "Confidence"],
            [recoverable, "Not counted", confidence],
        )
    if semantics == "one_time":
        return (
            ["Recoverable", "Type", "Confidence"],
            [recoverable, "One-time", confidence],
        )
    return (
        ["Annualized", "Monthly", "Confidence"],
        [
            _format_currency(finding["estimated_arr_loss"]),
            _format_currency(finding["estimated_monthly_loss"]),
            confidence,
        ],
    )


def _evidence_records_for_display(finding: dict[str, Any]) -> list[dict[str, Any]]:
    records = finding.get("evidence_records") or []
    semantics = finding.get("leakage_semantics")
    if semantics != "one_time":
        return records
    return [record for record in records if record.get("field") != "annual_leakage"]


class _BrandedDocTemplate(BaseDocTemplate):
    def __init__(
        self,
        buffer: io.BytesIO,
        *,
        report_id: str,
        company_name: str | None,
        **kwargs: Any,
    ) -> None:
        super().__init__(buffer, **kwargs)
        self.report_id = report_id
        self.company_name = company_name or "Your organization"
        frame = Frame(
            self.leftMargin,
            self.bottomMargin + 0.35 * inch,
            self.width,
            self.height - 0.35 * inch,
            id="normal",
        )
        self.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=self._draw_page)])

    def _draw_page(self, canvas: Any, doc: Any) -> None:
        canvas.saveState()
        width, height = letter

        canvas.setFillColor(SLATE_900)
        canvas.rect(0, height - 0.42 * inch, width, 0.42 * inch, fill=1, stroke=0)

        logo = _logo_path()
        if logo:
            canvas.drawImage(
                str(logo),
                doc.leftMargin,
                height - 0.36 * inch,
                width=1.35 * inch,
                height=0.28 * inch,
                preserveAspectRatio=True,
                mask="auto",
            )
        else:
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 11)
            canvas.drawString(doc.leftMargin, height - 0.28 * inch, "Paevo")

        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawRightString(
            width - doc.rightMargin,
            height - 0.27 * inch,
            "Revenue Leakage Radar",
        )

        canvas.setStrokeColor(SLATE_200)
        canvas.setLineWidth(0.5)
        canvas.line(
            doc.leftMargin,
            doc.bottomMargin + 0.2 * inch,
            width - doc.rightMargin,
            doc.bottomMargin + 0.2 * inch,
        )

        canvas.setFillColor(SLATE_500)
        canvas.setFont("Helvetica", 7)
        footer_left = f"Confidential · Prepared by Paevo · {self.company_name}"
        canvas.drawString(doc.leftMargin, doc.bottomMargin + 0.05 * inch, footer_left)
        canvas.drawRightString(
            width - doc.rightMargin,
            doc.bottomMargin + 0.05 * inch,
            f"Report {self.report_id[:8].upper()} · Page {doc.page}",
        )
        canvas.restoreState()


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "overline": ParagraphStyle(
            "Overline",
            parent=base["Normal"],
            fontSize=7.5,
            leading=10,
            textColor=SLATE_500,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        ),
        "title": ParagraphStyle(
            "Title",
            parent=base["Heading1"],
            fontSize=24,
            leading=28,
            spaceAfter=10,
            textColor=SLATE_900,
            fontName="Helvetica-Bold",
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontSize=10.5,
            leading=15,
            textColor=SLATE_700,
            spaceAfter=14,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=base["Heading2"],
            fontSize=14,
            leading=17,
            spaceBefore=16,
            spaceAfter=8,
            textColor=SLATE_900,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontSize=9.5,
            leading=13,
            textColor=SLATE_700,
        ),
        "metric_xl": ParagraphStyle(
            "MetricXL",
            parent=base["Normal"],
            fontSize=30,
            leading=32,
            textColor=SLATE_900,
            fontName="Helvetica-Bold",
        ),
        "finding_title": ParagraphStyle(
            "FindingTitle",
            parent=base["Heading3"],
            fontSize=13,
            leading=16,
            textColor=SLATE_900,
            fontName="Helvetica-Bold",
            spaceAfter=6,
        ),
        "label": ParagraphStyle(
            "Label",
            parent=base["Normal"],
            fontSize=7.5,
            leading=10,
            textColor=SLATE_500,
            fontName="Helvetica-Bold",
        ),
        "value": ParagraphStyle(
            "Value",
            parent=base["Normal"],
            fontSize=10.5,
            leading=13,
            textColor=SLATE_900,
            fontName="Helvetica-Bold",
        ),
        "recommendation": ParagraphStyle(
            "Recommendation",
            parent=base["BodyText"],
            fontSize=9.5,
            leading=13,
            textColor=SLATE_900,
            leftIndent=10,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["Normal"],
            fontSize=7.5,
            leading=10,
            textColor=SLATE_900,
            fontName="Helvetica-Bold",
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=SLATE_700,
            wordWrap="CJK",
        ),
        "table_cell_bold": ParagraphStyle(
            "TableCellBold",
            parent=base["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=SLATE_900,
            fontName="Helvetica-Bold",
            wordWrap="CJK",
        ),
        "table_link": ParagraphStyle(
            "TableLink",
            parent=base["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=ACCENT_BLUE,
            wordWrap="CJK",
        ),
        "table_mono": ParagraphStyle(
            "TableMono",
            parent=base["Normal"],
            fontSize=7.5,
            leading=10,
            textColor=SLATE_700,
            fontName="Courier",
            wordWrap="CJK",
        ),
        "category_header": ParagraphStyle(
            "CategoryHeader",
            parent=base["Normal"],
            fontSize=9.5,
            leading=12,
            textColor=SLATE_900,
            fontName="Helvetica-Bold",
            spaceBefore=6,
            spaceAfter=4,
        ),
        "inline_link": ParagraphStyle(
            "InlineLink",
            parent=base["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=ACCENT_BLUE,
        ),
        "anchor": ParagraphStyle(
            "Anchor",
            parent=base["Normal"],
            fontSize=1,
            leading=1,
            textColor=colors.white,
        ),
    }


def _p(
    value: Any,
    styles: dict[str, ParagraphStyle],
    style_key: str = "table_cell",
) -> Paragraph:
    return Paragraph(_safe(value), styles[style_key])


def _data_table(
    rows: list[list[Any]],
    col_widths: list[float],
    styles: dict[str, ParagraphStyle],
    *,
    header: bool = True,
    repeat_rows: int = 0,
) -> Table:
    wrapped_rows: list[list[Any]] = []
    for row_index, row in enumerate(rows):
        wrapped_row: list[Any] = []
        for cell in row:
            if isinstance(cell, Paragraph):
                wrapped_row.append(cell)
            elif row_index == 0 and header:
                wrapped_row.append(_p(cell, styles, "table_header"))
            else:
                wrapped_row.append(_p(cell, styles, "table_cell"))
        wrapped_rows.append(wrapped_row)

    table = Table(
        wrapped_rows,
        colWidths=col_widths,
        repeatRows=repeat_rows,
        splitByRow=1,
    )
    commands: list[tuple[Any, ...]] = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, SLATE_200),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), SLATE_100),
                ("TEXTCOLOR", (0, 0), (-1, 0), SLATE_900),
            ]
        )
    table.setStyle(TableStyle(commands))
    return table


def _metric_card(label: str, value: str, styles: dict[str, ParagraphStyle], width: float) -> Table:
    card = Table(
        [[Paragraph(label.upper(), styles["label"]), Paragraph(_safe(value), styles["value"])]],
        colWidths=[width],
    )
    card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SLATE_50),
                ("BOX", (0, 0), (-1, -1), 0.5, SLATE_200),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return card


def _build_cover_section(detail: dict[str, Any], styles: dict[str, ParagraphStyle]) -> list[Any]:
    summary = detail["executive_summary"]
    company = detail.get("company_name") or "Your organization"
    period = _format_date(detail.get("generated_at"))
    confidence = summary.get("confidence")
    card_width = CONTENT_WIDTH / 4

    story: list[Any] = []
    story.append(
        Paragraph(
            f"CONFIDENTIAL · {_safe(company)} · {_safe(period)}",
            styles["overline"],
        )
    )
    story.append(Paragraph("Revenue Leakage Findings", styles["title"]))
    story.append(
        Paragraph(
            "An examination of billing, CRM, pricing, and subscription data, isolating "
            "recoverable revenue lost to verification failures over the reporting period.",
            styles["subtitle"],
        )
    )
    story.append(Paragraph("TOTAL RECOVERABLE REVENUE", styles["overline"]))
    story.append(Paragraph(_safe(_format_currency(summary["recoverable_arr"])), styles["metric_xl"]))
    narrative_bits = [f"{summary['finding_count']} distinct findings"]
    if confidence:
        narrative_bits.append(f"weighted confidence {confidence}%")
    reconciliation = summary.get("reconciliation") or {}
    secondary_excluded = reconciliation.get("secondary_excluded_arr")
    reconciliation_note = ""
    if secondary_excluded and Decimal(str(secondary_excluded)) > 0:
        reconciliation_note = (
            f" Primary recoverable ARR excludes {secondary_excluded} from overlapping secondary findings."
        )
    story.append(
        Paragraph(
            f"Identified across {', '.join(narrative_bits)}. "
            f"The headline figure sums primary-attributed forward recoverable ARR only.{reconciliation_note}",
            styles["body"],
        )
    )
    story.append(Spacer(1, 10))

    metric_row = Table(
        [
            [
                _metric_card("Accounts", str(summary["accounts_reviewed"]), styles, card_width),
                _metric_card("Invoices", str(summary["invoices_reviewed"]), styles, card_width),
                _metric_card("Findings", str(summary["finding_count"]), styles, card_width),
                _metric_card("Confidence", f"{confidence}%" if confidence else "-", styles, card_width),
            ],
            [
                _metric_card(
                    "High confidence",
                    _format_currency(summary["high_confidence_arr"]),
                    styles,
                    card_width,
                ),
                _metric_card(
                    "Medium confidence",
                    _format_currency(summary["medium_confidence_arr"]),
                    styles,
                    card_width,
                ),
                _metric_card(
                    "Low confidence",
                    _format_currency(summary["low_confidence_arr"]),
                    styles,
                    card_width,
                ),
                _metric_card(
                    "Rules executed",
                    f"{summary['rules_completed']}/{summary['rules_total']}",
                    styles,
                    card_width,
                ),
            ],
        ],
        colWidths=[card_width, card_width, card_width, card_width],
        hAlign="LEFT",
    )
    metric_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(metric_row)
    return story


def _build_executive_summary(summary: dict[str, Any], styles: dict[str, ParagraphStyle]) -> list[Any]:
    narrative = summary.get("narrative", "")
    if not narrative:
        return []
    return [
        Paragraph("Executive Summary", styles["section"]),
        Paragraph(_safe(narrative), styles["body"]),
        Spacer(1, 8),
    ]


def _build_opportunity_section(
    breakdown: list[dict[str, Any]],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    if not breakdown:
        return []
    rows = [["Category", "Recoverable ARR", "Issues", "Accounts", "Confidence"]]
    for row in breakdown:
        rows.append(
            [
                row["label"],
                _format_currency(row["arr"]),
                str(row["issue_count"]),
                str(row.get("account_count", "-")),
                f"{row['confidence']}%" if row.get("confidence") else "-",
            ]
        )
    table = _data_table(rows, _col_widths(3.2, 1.6, 1.0, 1.1, 1.1), styles)
    return [
        Paragraph("Where It Leaks", styles["section"]),
        Paragraph(
            "Recoverable ARR grouped by verification category. Addressing the highest-impact "
            "categories first captures the majority of total recoverable revenue.",
            styles["body"],
        ),
        Spacer(1, 8),
        table,
        Spacer(1, 10),
    ]


def _build_verification_section(
    checks: list[dict[str, Any]],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    if not checks:
        return []
    rows = [["Verification Rule", "Status", "Findings", "Primary ARR", "Notes"]]
    for check in checks:
        note = check.get("coverage_note") or check.get("skip_reason") or "-"
        primary_count = check.get("primary_finding_count", check["finding_count"])
        total_count = check["finding_count"]
        findings_label = (
            str(total_count)
            if primary_count == total_count
            else f"{total_count} ({primary_count} primary)"
        )
        rows.append(
            [
                check["name"],
                STATUS_LABELS.get(check["status"], check["status"]),
                findings_label,
                _format_currency(check["arr"]),
                note,
            ]
        )
    table = _data_table(rows, _col_widths(2.5, 1.1, 1.0, 1.0, 2.4), styles)
    return [
        PageBreak(),
        Paragraph("Verification Checks", styles["section"]),
        Paragraph(
            "Deterministic rules executed against the supplied dataset. Primary ARR counts "
            "only headline-eligible findings; overlapping secondary findings are excluded "
            "from totals but remain in the detailed evidence section.",
            styles["body"],
        ),
        Spacer(1, 8),
        table,
        Spacer(1, 10),
    ]


def _severity_cell(severity: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    color = _hex(_severity_color(severity))
    return Paragraph(
        f'<font color="{color}"><b>{_safe(severity.title())}</b></font>',
        styles["table_cell"],
    )


def _finding_link(title: str, anchor: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(
        f'<a href="#{anchor}" color="{_hex(ACCENT_BLUE)}">{_safe(title)}</a>',
        styles["table_link"],
    )


def _back_to_index_link(styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(
        f'<a href="#{INDEX_ANCHOR}" color="{_hex(ACCENT_BLUE)}">← Back to findings index</a>',
        styles["inline_link"],
    )


def _build_findings_index(
    findings: list[dict[str, Any]],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    if not findings:
        return [Paragraph("No findings in this report.", styles["body"])]

    prepared = _prepare_findings_for_report(findings)
    primary_count = sum(1 for finding in prepared if finding.get("attribution") != "secondary")

    story: list[Any] = [
        PageBreak(),
        Paragraph(f'<a name="{INDEX_ANCHOR}"/>', styles["anchor"]),
        Paragraph("Findings Index", styles["section"]),
        Paragraph(
            f"{len(prepared)} evidence-backed issues organized by category "
            f"({primary_count} primary, {len(prepared) - primary_count} overlapping secondary). "
            "ARR totals below count primary recoverable amounts only. "
            "Select a finding title to jump to its detailed evidence page.",
            styles["body"],
        ),
        Spacer(1, 10),
    ]

    for category_label, category_findings in _group_findings_by_category(prepared):
        primary_in_category = sum(
            1 for row in category_findings if row.get("attribution") != "secondary"
        )
        category_arr = _format_currency(
            sum(_primary_recoverable_amount(row) for row in category_findings)
        )
        count_note = (
            f"{len(category_findings)} finding{'s' if len(category_findings) != 1 else ''}"
            if primary_in_category == len(category_findings)
            else (
                f"{len(category_findings)} findings "
                f"({primary_in_category} primary)"
            )
        )
        story.append(
            Paragraph(
                f"{_safe(category_label)} · {count_note} · {category_arr} primary ARR",
                styles["category_header"],
            )
        )

        rows: list[list[Any]] = [["#", "Finding", "Severity", "ARR", "Conf."]]
        for finding in category_findings:
            anchor = _finding_anchor(finding["id"])
            arr_label = (
                _format_currency(finding.get("recoverable_amount") or _recoverable_amount(finding))
                if finding.get("attribution") != "secondary"
                else "Excluded"
            )
            rows.append(
                [
                    str(finding["report_index"]),
                    _finding_link(finding["title"], anchor, styles),
                    _severity_cell(finding.get("severity", "medium"), styles),
                    arr_label,
                    f"{finding['confidence']}%",
                ]
            )

        table = _data_table(rows, _col_widths(0.45, 3.6, 1.0, 1.1, 0.85), styles)
        story.extend([table, Spacer(1, 10)])

    return story


def _mono_cell(value: Any, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(_safe(value), styles["table_mono"])


def _build_entity_table(
    finding: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table | None:
    entity_rows: list[list[Any]] = [["Entity", "Source system ID"]]
    if finding.get("customer_id"):
        entity_rows.append(["Customer", _mono_cell(finding["customer_id"], styles)])
    if finding.get("subscription_id"):
        entity_rows.append(["Subscription", _mono_cell(finding["subscription_id"], styles)])
    if finding.get("invoice_id"):
        entity_rows.append(["Invoice", _mono_cell(finding["invoice_id"], styles)])
    if len(entity_rows) == 1:
        return None
    return _data_table(entity_rows, _col_widths(1.1, 4.9), styles, repeat_rows=1)


def _build_evidence_table(
    records: list[dict[str, Any]],
    styles: dict[str, ParagraphStyle],
) -> Table:
    evidence_rows: list[list[Any]] = [["Field", "Expected", "Actual", "References"]]
    for record in records:
        evidence_rows.append(
            [
                record.get("field", ""),
                _mono_cell(format_decimal_display(record.get("expected")) or "-", styles),
                _mono_cell(format_decimal_display(record.get("actual")) or "-", styles),
                _mono_cell(_reference_ids_text(record.get("reference_ids")), styles),
            ]
        )
    return _data_table(
        evidence_rows,
        _col_widths(1.2, 1.5, 1.5, 2.8),
        styles,
        repeat_rows=1,
    )


def _reference_ids_text(reference_ids: dict[str, str] | None) -> str:
    if not reference_ids:
        return "-"
    return ", ".join(f"{key}: {value}" for key, value in reference_ids.items())


def _build_finding_detail(
    index: int,
    finding: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    anchor = _finding_anchor(finding["id"])
    severity = finding.get("severity", "medium")
    rule_id = finding.get("rule_id") or finding["id"][:8].upper()
    attribution_note = ""
    if finding.get("attribution") == "secondary":
        attribution_note = " · Secondary overlap (excluded from headline ARR)"

    header_bits = (
        f'<font color="{_hex(_severity_color(severity))}"><b>{_safe(severity.upper())}</b></font>'
        f" · {_safe(finding.get('category_label', finding.get('category', '')))}"
        f' · <font color="{_hex(SLATE_500)}">{_safe(rule_id)}</font>'
        f"{_safe(attribution_note)}"
    )

    block: list[Any] = [
        PageBreak(),
        Paragraph(f'<a name="{anchor}"/>', styles["anchor"]),
        _back_to_index_link(styles),
        Spacer(1, 6),
        Paragraph(f"FINDING {index}", styles["overline"]),
        Paragraph(header_bits, styles["body"]),
        Paragraph(_safe(finding["title"]), styles["finding_title"]),
    ]

    metric_headers, metric_values = _finding_metrics_table(finding)
    metrics = _data_table(
        [metric_headers, metric_values],
        _col_widths(1, 1, 1),
        styles,
        header=True,
        repeat_rows=1,
    )
    block.extend([metrics, Spacer(1, 8)])

    if finding.get("attribution") == "secondary":
        primary_title = finding.get("primary_finding_title")
        if primary_title:
            block.append(
                Paragraph(
                    _safe(
                        f"Excluded from headline recoverable ARR because the same leakage is "
                        f'counted under primary finding "{primary_title}".'
                    ),
                    styles["body"],
                )
            )
            block.append(Spacer(1, 8))

    entity_table = _build_entity_table(finding, styles)
    if entity_table is not None:
        block.extend([Paragraph("Affected Entities", styles["label"]), entity_table, Spacer(1, 8)])

    recommendation = finding.get("recommendation")
    if recommendation:
        remedy_box = Table(
            [[Paragraph(_safe(recommendation), styles["recommendation"])]],
            colWidths=[CONTENT_WIDTH],
        )
        remedy_box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), SLATE_50),
                    ("BOX", (0, 0), (-1, -1), 0.5, SLATE_200),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("LINEBEFORE", (0, 0), (0, -1), 2, ACCENT_BLUE),
                ]
            )
        )
        block.extend(
            [
                Paragraph(
                    f'<font color="{_hex(ACCENT_BLUE)}">RECOMMENDED REMEDY</font>',
                    styles["label"],
                ),
                remedy_box,
                Spacer(1, 8),
            ]
        )

    records = _evidence_records_for_display(finding)
    if records:
        block.extend(
            [
                Paragraph("Evidence", styles["label"]),
                _build_evidence_table(records, styles),
            ]
        )
    else:
        block.append(Paragraph("No detailed evidence records for this finding.", styles["body"]))

    block.append(Spacer(1, 12))
    return block


def _build_findings_detail_section(
    findings: list[dict[str, Any]],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    if not findings:
        return []

    prepared = _prepare_findings_for_report(findings)

    story: list[Any] = [
        Paragraph("Finding Details", styles["section"]),
        Paragraph(
            "Full evidence, entity references, and remediation guidance for each finding. "
            "Finding numbers match the index and are ordered by recoverable impact.",
            styles["body"],
        ),
        Spacer(1, 6),
    ]

    for finding in prepared:
        story.extend(_build_finding_detail(finding["report_index"], finding, styles))

    story.append(
        Paragraph(
            "Prepared by Paevo. Figures are estimates derived from the supplied data "
            "and intended for internal review.",
            styles["body"],
        )
    )
    return story


def build_report_pdf(db: Session, report: Report) -> bytes:
    detail = build_report_detail(db, report, evidence_record_limit=None, include_findings=True)
    styles = _build_styles()
    buffer = io.BytesIO()

    doc = _BrandedDocTemplate(
        buffer,
        report_id=str(detail["id"]),
        company_name=detail.get("company_name"),
        pagesize=letter,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        title="Revenue Leakage Findings",
        author="Paevo",
    )

    story: list[Any] = []
    story.extend(_build_cover_section(detail, styles))
    story.extend(_build_executive_summary(detail["executive_summary"], styles))
    story.extend(_build_opportunity_section(detail["opportunity_breakdown"], styles))
    story.extend(_build_verification_section(detail["verification_checks"], styles))
    story.extend(_build_findings_index(detail["findings"], styles))
    story.extend(_build_findings_detail_section(detail["findings"], styles))

    doc.build(story)
    return buffer.getvalue()
