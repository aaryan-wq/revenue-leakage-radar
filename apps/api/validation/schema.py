from canonical.fields import PRIMARY_KEY_FIELDS, REQUIRED_CANONICAL_FIELDS
from core.enums import FileType, REQUIRED_BILLING_FILE_TYPES
from ingestion.types import ValidationIssue, ValidationReport


def validate_schema(frames: dict[FileType, object], report: ValidationReport) -> None:
    for required_type in REQUIRED_BILLING_FILE_TYPES:
        if required_type not in frames:
            report.issues.append(
                ValidationIssue(
                    severity="blocking",
                    code="missing_file",
                    message=f"Required file missing: {required_type.value}",
                    file_type=required_type.value,
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

        pk_field = PRIMARY_KEY_FIELDS.get(file_type)
        if pk_field and pk_field in columns:
            null_count = df[pk_field].null_count()
            if null_count > 0:
                report.issues.append(
                    ValidationIssue(
                        severity="blocking",
                        code="null_primary_key",
                        message=f"{null_count} rows with null {pk_field} in {file_type.value}",
                        file_type=file_type.value,
                        field=pk_field,
                    )
                )
