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


def validate_dates(frames: dict[FileType, pl.DataFrame], report: ValidationReport) -> None:
    for file_type, df in frames.items():
        for field in DATE_FIELDS:
            if field not in df.columns:
                continue

            bad_rows = 0
            for value in df[field].to_list():
                if value is None or str(value).strip() == "":
                    continue
                if _parse_date(str(value)) is None:
                    bad_rows += 1

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
