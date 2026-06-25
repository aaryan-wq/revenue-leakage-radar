from core.enums import FileType
from ingestion.types import ValidationReport
from validation.currency import validate_currency
from validation.dates import validate_dates
from validation.duplicates import validate_duplicates
from validation.relationships import validate_relationships
from validation.schema import validate_schema


def run_validation(frames: dict[FileType, object]) -> ValidationReport:
    report = ValidationReport()

    validate_schema(frames, report)
    validate_duplicates(frames, report)
    validate_dates(frames, report)
    validate_currency(frames, report)
    validate_relationships(frames, report)

    report.summary = {
        "file_count": len(frames),
        "issue_count": len(report.issues),
        "blocking_count": sum(1 for i in report.issues if i.severity == "blocking"),
        "warning_count": sum(1 for i in report.issues if i.severity == "warning"),
    }

    return report
