import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from core.enums import AuditStatus
from verification.engine.pipeline import run_verification_engine
from verification.types import RuleFinding, ScanReport


@pytest.fixture
def mock_audit():
    audit = MagicMock()
    audit.id = uuid.uuid4()
    audit.company_id = uuid.uuid4()
    audit.status = AuditStatus.READY_FOR_SCAN.value
    audit.scan_report = None
    audit.scan_error = None
    return audit


def _sample_finding() -> RuleFinding:
    return RuleFinding(
        rule_id="test_rule",
        rule_name="Test Rule",
        title="Test",
        severity="high",
        confidence=Decimal("90"),
        estimated_monthly_loss=Decimal("10"),
        estimated_arr_loss=Decimal("120"),
        recommendation="Fix it",
    )


@patch("verification.engine.pipeline.upsert_report")
@patch("verification.engine.pipeline.persist_findings")
@patch("verification.engine.pipeline.clear_findings")
@patch("verification.engine.pipeline.load_audit_context")
@patch("verification.engine.pipeline.transition_audit_status")
@patch("verification.engine.pipeline.run_engine")
def test_engine_runs_and_persists(
    mock_run_engine,
    mock_transition,
    mock_load_ctx,
    mock_clear,
    mock_persist,
    mock_upsert,
    mock_audit,
):
    from models import Finding

    mock_ctx = MagicMock()
    mock_ctx.data_tier = MagicMock(value="tier_0")
    mock_load_ctx.return_value = mock_ctx
    mock_run_engine.return_value = (
        [_sample_finding()],
        ScanReport(
            rules_total=1,
            rules_completed=1,
            rules_skipped=0,
            rules_partial=0,
            rules_errored=0,
            finding_count=1,
            recoverable_arr="120",
            overall_confidence="90",
            data_tier="tier_0",
            rule_logs=[],
        ),
    )

    mock_finding = Finding(
        id=uuid.uuid4(),
        audit_id=mock_audit.id,
        rule_id="test",
        severity="high",
        confidence=Decimal("90"),
        estimated_monthly_loss=Decimal("10"),
        estimated_arr_loss=Decimal("120"),
    )
    mock_persist.return_value = [mock_finding]

    db = MagicMock()
    report = run_verification_engine(db, mock_audit)

    assert report.finding_count == 1
    mock_clear.assert_called_once()
    mock_persist.assert_called_once()
    mock_upsert.assert_called_once()
    assert mock_transition.call_count >= 2


@patch("verification.engine.pipeline.upsert_report")
@patch("verification.engine.pipeline.persist_findings")
@patch("verification.engine.pipeline.clear_findings")
@patch("verification.engine.pipeline.load_audit_context")
@patch("verification.engine.pipeline.transition_audit_status")
@patch("verification.engine.pipeline.run_engine")
def test_engine_skips_when_required_entities_missing(
    mock_run_engine,
    mock_transition,
    mock_load_ctx,
    mock_clear,
    mock_persist,
    mock_upsert,
    mock_audit,
):
    mock_ctx = MagicMock()
    mock_ctx.data_tier = MagicMock(value="insufficient")
    mock_load_ctx.return_value = mock_ctx
    mock_run_engine.return_value = (
        [],
        ScanReport(
            rules_total=1,
            rules_completed=0,
            rules_skipped=1,
            rules_partial=0,
            rules_errored=0,
            finding_count=0,
            recoverable_arr="0",
            overall_confidence=None,
            data_tier="insufficient",
            rule_logs=[],
        ),
    )
    mock_persist.return_value = []

    db = MagicMock()
    report = run_verification_engine(db, mock_audit)

    assert report.rules_skipped == 1
    assert report.finding_count == 0
