from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from audit.service import can_trigger_scan, get_scan_response, get_validation_response, trigger_verification
from core.enums import AuditStatus, ValidationResult
from models import Audit


def _audit(status: str, validation_result: str | None = "ready") -> Audit:
    audit = Audit(session_token="test-token")
    audit.status = status
    audit.validation_result = validation_result
    return audit


def test_can_trigger_scan_when_ready():
    audit = _audit(AuditStatus.READY_FOR_SCAN.value)
    can_run, reason = can_trigger_scan(audit)
    assert can_run is True
    assert reason is None


def test_can_retry_scan_after_processing_failed():
    audit = _audit(AuditStatus.PROCESSING_FAILED.value)
    audit.scan_error = "Verification scan failed. Please try again."
    can_run, reason = can_trigger_scan(audit)
    assert can_run is True
    assert reason is None


def test_validation_allows_scan_after_processing_failed():
    audit = _audit(AuditStatus.PROCESSING_FAILED.value)
    audit.scan_error = "Verification scan failed. Please try again."
    data = get_validation_response(audit)
    assert data["can_proceed_to_scan"] is True


def test_cannot_trigger_scan_when_blocking():
    audit = _audit(AuditStatus.READY_FOR_SCAN.value, ValidationResult.BLOCKING.value)
    can_run, reason = can_trigger_scan(audit)
    assert can_run is False
    assert reason is not None


def test_cannot_trigger_scan_when_completed():
    audit = _audit(AuditStatus.COMPLETED.value)
    can_run, reason = can_trigger_scan(audit)
    assert can_run is False


def test_get_scan_response_defaults():
    audit = _audit(AuditStatus.COMPLETED.value)
    audit.scan_report = {
        "finding_count": 5,
        "recoverable_arr": "12000",
        "rules_completed": 18,
        "rules_total": 20,
    }
    data = get_scan_response(audit)
    assert data["finding_count"] == 5
    assert data["recoverable_arr"] == "12000"


@patch("workers.tasks.verification.run_verification_task")
def test_trigger_verification_is_idempotent_when_scan_in_progress(mock_task):
    audit = _audit(AuditStatus.SCANNING.value)
    audit.updated_at = datetime.now(timezone.utc)
    trigger_verification(MagicMock(), audit)
    mock_task.delay.assert_not_called()


@patch("workers.tasks.verification.run_verification_task")
def test_trigger_verification_is_idempotent_when_completed(mock_task):
    audit = _audit(AuditStatus.COMPLETED.value)
    trigger_verification(MagicMock(), audit)
    mock_task.delay.assert_not_called()
