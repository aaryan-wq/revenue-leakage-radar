"""Tests for vectorized date validation."""

from __future__ import annotations

import polars as pl

from core.enums import FileType
from ingestion.types import ValidationReport
from validation.dates import validate_dates


def test_validate_dates_flags_unparseable_values():
    frames = {
        FileType.SUBSCRIPTIONS: pl.DataFrame(
            {
                "start_date": ["2024-01-01", "not-a-date", ""],
                "renewal_date": ["2024-06-01", "2024-06-01", "2024-06-01"],
            }
        )
    }
    report = ValidationReport()
    validate_dates(frames, report)

    assert len(report.issues) == 1
    assert report.issues[0].code == "invalid_date"
    assert report.issues[0].field == "start_date"
    assert "1 rows" in report.issues[0].message


def test_validate_dates_accepts_common_formats():
    frames = {
        FileType.INVOICES: pl.DataFrame(
            {
                "invoice_date": ["2024-01-01", "2024-12-31"],
            }
        )
    }
    report = ValidationReport()
    validate_dates(frames, report)
    assert report.issues == []
