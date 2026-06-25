import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from core.enums import AuditStatus
from verification.engine import run_verification_engine
from verification.types import RuleFinding


@pytest.fixture
def mock_audit():
    audit = MagicMock()
    audit.id = uuid.uuid4()
    audit.company_id = uuid.uuid4()
    audit.status = AuditStatus.READY_FOR_SCAN.value
    audit.scan_report = None
    audit.scan_error = None
    return audit


@patch("verification.engine.upsert_report")
@patch("verification.engine.persist_findings")
@patch("verification.engine.clear_findings")
@patch("verification.engine.load_audit_context")
@patch("verification.engine.transition_audit_status")
def test_engine_runs_and_persists(
    mock_transition,
    mock_load_ctx,
    mock_clear,
    mock_persist,
    mock_upsert,
    mock_audit,
):
    from models import Finding

    mock_load_ctx.return_value = MagicMock(
        has_crm=False,
        has_credit_data=False,
        has_manual_override_data=False,
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

    with patch("verification.engine.get_all_rules") as mock_rules:
        rule = MagicMock()
        rule.rule_id = "test_rule"
        rule.requires_crm = False
        rule.requires_credit_data = False
        rule.requires_manual_override = False
        rule.evaluate.return_value = [
            RuleFinding(
                rule_id="test_rule",
                title="Test",
                severity="high",
                confidence=Decimal("90"),
                estimated_monthly_loss=Decimal("10"),
                estimated_arr_loss=Decimal("120"),
                recommendation="Fix it",
            )
        ]
        mock_rules.return_value = [rule]

        report = run_verification_engine(db, mock_audit)

    assert report.finding_count == 1
    mock_clear.assert_called_once()
    mock_persist.assert_called_once()
    mock_upsert.assert_called_once()
    assert mock_transition.call_count >= 2
