from core.data_tiers import get_audit_data_tier, missing_recommended_files
from core.enums import FileType
from ingestion.types import ValidationReport
from validation.currency import validate_currency
from validation.dates import validate_dates
from validation.duplicates import validate_duplicates
from validation.relationships import validate_relationships
from validation.schema import validate_schema


def run_validation(
    frames: dict[FileType, object],
    uploaded: set[FileType] | None = None,
) -> ValidationReport:
    report = ValidationReport()
    uploaded_types = uploaded if uploaded is not None else set(frames.keys())

    validate_schema(frames, report, uploaded_types)
    validate_duplicates(frames, report)
    validate_dates(frames, report)
    validate_currency(frames, report)
    validate_relationships(frames, report, uploaded_types)

    report.summary = {
        "file_count": len(frames),
        "issue_count": len(report.issues),
        "blocking_count": sum(1 for i in report.issues if i.severity == "blocking"),
        "warning_count": sum(1 for i in report.issues if i.severity == "warning"),
        "data_tier": get_audit_data_tier(uploaded_types).value,
        "recommended_missing": [ft.value for ft in missing_recommended_files(uploaded_types)],
    }

    return report
