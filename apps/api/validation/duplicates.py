import polars as pl

from canonical.fields import PRIMARY_KEY_FIELDS
from core.enums import FileType
from ingestion.types import ValidationIssue, ValidationReport


def validate_duplicates(frames: dict[FileType, object], report: ValidationReport) -> None:
    for file_type, df in frames.items():
        pk_field = PRIMARY_KEY_FIELDS.get(file_type)
        if not pk_field or pk_field not in df.columns:
            continue

        duplicates = (
            df.group_by(pk_field)
            .len()
            .filter(pl.col("len") > 1)
        )
        if duplicates.height > 0:
            dup_ids = duplicates[pk_field].to_list()[:5]
            report.issues.append(
                ValidationIssue(
                    severity="blocking",
                    code="duplicate_primary_key",
                    message=f"Duplicate {pk_field} values found: {dup_ids}",
                    file_type=file_type.value,
                    field=pk_field,
                )
            )
