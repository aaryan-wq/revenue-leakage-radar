from dataclasses import dataclass, field
from typing import Any

import polars as pl

from core.canonical_entities import CanonicalEntity
from core.enums import FileType, Platform, ValidationResult


@dataclass
class ColumnMapping:
    source_header: str
    canonical_field: str
    confidence: float = 1.0


@dataclass
class ValidationIssue:
    severity: str
    code: str
    message: str
    file_type: str | None = None
    field: str | None = None
    row: int | None = None


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)
    row_errors: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    @property
    def has_blocking(self) -> bool:
        return any(issue.severity == "blocking" for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(issue.severity == "warning" for issue in self.issues)

    def to_dict(self) -> dict[str, Any]:
        return {
            "issues": [
                {
                    "severity": i.severity,
                    "code": i.code,
                    "message": i.message,
                    "file_type": i.file_type,
                    "field": i.field,
                    "row": i.row,
                }
                for i in self.issues
            ],
            "row_errors": self.row_errors,
            "summary": self.summary,
        }

    def result(self) -> ValidationResult:
        if self.has_blocking:
            return ValidationResult.BLOCKING
        if self.has_warnings:
            return ValidationResult.WARNINGS
        return ValidationResult.READY


@dataclass
class IngestionContext:
    audit_id: str
    platform: Platform = Platform.GENERIC
    column_mappings: dict[str, dict[str, str]] = field(default_factory=dict)
    frames: dict[FileType, pl.DataFrame] = field(default_factory=dict)
    validation_report: ValidationReport = field(default_factory=ValidationReport)
    uploaded_file_types: set[FileType] = field(default_factory=set)
    available_entities: set[CanonicalEntity] = field(default_factory=set)

    def get_mapping(self, file_type: FileType) -> dict[str, str]:
        return self.column_mappings.get(file_type.value, {})
