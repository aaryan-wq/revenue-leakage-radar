from canonical.fields import REQUIRED_CANONICAL_FIELDS, primary_key_columns
from core.data_tiers import missing_recommended_files
from core.enums import FileType
from ingestion.types import ValidationIssue, ValidationReport


def validate_schema(
    frames: dict[FileType, object],
    report: ValidationReport,
    uploaded: set[FileType] | None = None,
) -> None:
    uploaded_types = uploaded if uploaded is not None else set(frames.keys())

    if not uploaded_types:
        report.issues.append(
            ValidationIssue(
                severity="blocking",
                code="no_uploads",
                message="Upload at least one billing export to continue.",
            )
        )

    for recommended in missing_recommended_files(uploaded_types):
        report.issues.append(
            ValidationIssue(
                severity="warning",
                code="missing_recommended_file",
                message=f"Recommended file missing: {recommended.value}",
                file_type=recommended.value,
            )
        )

    for file_type, df in frames.items():
        required_fields = REQUIRED_CANONICAL_FIELDS.get(file_type, [])
        columns = set(df.columns)

        for field in required_fields:
            if field not in columns:
                report.issues.append(
                    ValidationIssue(
                        severity="blocking",
                        code="missing_column",
                        message=f"Required column '{field}' not mapped in {file_type.value}",
                        file_type=file_type.value,
                        field=field,
                    )
                )

        key_columns = primary_key_columns(file_type)
        if key_columns and all(field in columns for field in key_columns):
            for field in key_columns:
                null_count = df[field].null_count()
                if null_count > 0:
                    report.issues.append(
                        ValidationIssue(
                            severity="blocking",
                            code="null_primary_key",
                            message=f"{null_count} rows with null {field} in {file_type.value}",
                            file_type=file_type.value,
                            field=field,
                        )
                    )
