import polars as pl

from canonical.fields import primary_key_columns
from core.enums import FileType
from ingestion.types import ValidationIssue, ValidationReport


def validate_duplicates(frames: dict[FileType, object], report: ValidationReport) -> None:
    for file_type, df in frames.items():
        key_columns = primary_key_columns(file_type)
        if not key_columns or not all(column in df.columns for column in key_columns):
            continue

        duplicates = df.group_by(key_columns).len().filter(pl.col("len") > 1)
        if duplicates.height > 0:
            if len(key_columns) == 1:
                dup_ids = duplicates[key_columns[0]].to_list()[:5]
                message = f"Duplicate {key_columns[0]} values found: {dup_ids}"
            else:
                key_label = ", ".join(key_columns)
                dup_rows = duplicates.select(key_columns).head(5).to_dicts()
                message = f"Duplicate ({key_label}) combinations found: {dup_rows}"
            report.issues.append(
                ValidationIssue(
                    severity="blocking",
                    code="duplicate_primary_key",
                    message=message,
                    file_type=file_type.value,
                    field=key_columns[0],
                )
            )
