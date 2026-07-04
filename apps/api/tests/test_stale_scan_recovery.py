import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from audit.service import recover_stale_scan_if_needed, trigger_verification
from core.enums import AuditStatus
from models import Audit


@patch("workers.tasks.verification.run_verification_task")
@patch("core.config.settings")
def test_recovers_stale_scanning_state_in_eager_mode(mock_settings, mock_task):
    mock_settings.celery_task_always_eager = True
    audit = Audit(session_token="token", status=AuditStatus.SCANNING.value)
    audit.id = uuid.uuid4()
    audit.validation_result = "ready"
    audit.updated_at = datetime.now(timezone.utc) - timedelta(seconds=120)
    db = MagicMock()
    execute_result = MagicMock()
    execute_result.rowcount = 1
    db.execute.return_value = execute_result

    trigger_verification(db, audit)

    assert audit.status == AuditStatus.READY_FOR_SCAN.value
    mock_task.delay.assert_called_once_with(str(audit.id))


@patch("core.config.settings")
def test_does_not_recover_recent_scan_without_eager(mock_settings):
    mock_settings.celery_task_always_eager = False
    audit = Audit(session_token="token", status=AuditStatus.SCANNING.value)
    audit.updated_at = datetime.now(timezone.utc)
    db = MagicMock()

    recovered = recover_stale_scan_if_needed(db, audit)

    assert recovered is False
    db.commit.assert_not_called()
