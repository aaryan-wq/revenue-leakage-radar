from audit.service import can_trigger_scan, get_scan_response
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
