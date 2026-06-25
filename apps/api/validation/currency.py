import polars as pl

from core.enums import FileType
from ingestion.types import ValidationIssue, ValidationReport


def validate_currency(frames: dict[FileType, pl.DataFrame], report: ValidationReport) -> None:
    currencies: set[str] = set()

    for file_type, df in frames.items():
        if "currency" not in df.columns:
            continue
        for value in df["currency"].drop_nulls().to_list():
            currencies.add(str(value).strip().upper())

    if len(currencies) > 1:
        report.issues.append(
            ValidationIssue(
                severity="warning",
                code="currency_mismatch",
                message=f"Multiple currencies detected: {sorted(currencies)}",
            )
        )
