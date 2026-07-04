from verification.formatting import (
    format_decimal_display,
    normalize_calculation_trace,
    normalize_evidence_records,
)


def test_format_decimal_display_strips_extra_precision():
    assert format_decimal_display("185.4400") == "185.44"
    assert format_decimal_display("12.0000") == "12"
    assert format_decimal_display("70.00") == "70"


def test_normalize_evidence_records():
    records = normalize_evidence_records(
        [{"field": "unit_price", "expected": "247.2500", "actual": "185.4400"}]
    )
    assert records[0]["expected"] == "247.25"
    assert records[0]["actual"] == "185.44"


def test_normalize_calculation_trace():
    trace = normalize_calculation_trace(
        {
            "steps": [{"step_id": "difference", "label": "Difference", "value": "61.8100"}],
            "result_monthly": "741.7500",
            "result_annual": "8901.0000",
            "semantics": "recurring_run_rate",
        }
    )
    assert trace["steps"][0]["value"] == "61.81"
    assert trace["result_monthly"] == "741.75"
    assert trace["result_annual"] == "8901"
