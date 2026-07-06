from datetime import datetime

import polars as pl

from core.enums import FileType
from ingestion.types import ValidationIssue, ValidationReport

DATE_FIELDS = {
    "start_date",
    "renewal_date",
    "invoice_date",
    "period_start",
    "period_end",
    "effective_date",
    "expires_at",
}


def _parse_date(value: str) -> datetime | None:
    if not value or value.lower() in ("null", "none", ""):
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y"):
        try:
            return datetime.strptime(value[:19], fmt)
        except ValueError:
            continue
    return None


def _count_unparseable_dates(series: pl.Series) -> int:
    if series.len() == 0:
        return 0
    as_text = series.cast(pl.Utf8, strict=False).fill_null("").str.strip_chars()
    present_mask = (as_text != "") & (as_text.str.to_lowercase() != "null")
    present = as_text.filter(present_mask)
    if present.len() == 0:
        return 0

    parsed_iso = present.str.to_date("%Y-%m-%d", strict=False)
    remaining = present.filter(parsed_iso.is_null())
    if remaining.len() == 0:
        return 0

    bad_rows = 0
    for value in remaining.to_list():
        if _parse_date(str(value)) is None:
            bad_rows += 1
    return bad_rows


def validate_dates(frames: dict[FileType, pl.DataFrame], report: ValidationReport) -> None:
    for file_type, df in frames.items():
        for field in DATE_FIELDS:
            if field not in df.columns:
                continue

            bad_rows = _count_unparseable_dates(df[field])
            if bad_rows > 0:
                report.issues.append(
                    ValidationIssue(
                        severity="warning",
                        code="invalid_date",
                        message=f"{bad_rows} rows with unparseable dates in {field}",
                        file_type=file_type.value,
                        field=field,
                    )
                )
