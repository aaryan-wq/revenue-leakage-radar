import uuid
from unittest.mock import MagicMock, patch

import pytest

from admin.service import admin_delete_report, admin_reprocess_audit
from core.enums import AuditStatus
from models import Audit, Report


def test_admin_delete_report_removes_row():
    report_id = uuid.uuid4()
    report = Report(audit_id=uuid.uuid4(), recoverable_arr=0, finding_count=0)
    report.id = report_id
    db = MagicMock()

    with patch("admin.service.get_report_by_id", return_value=report):
        admin_delete_report(db, report_id)

    db.delete.assert_called_once_with(report)
    db.commit.assert_called_once()


def test_admin_delete_report_missing():
    db = MagicMock()
    with patch("admin.service.get_report_by_id", return_value=None):
        with pytest.raises(ValueError, match="Report not found"):
            admin_delete_report(db, uuid.uuid4())


def test_admin_reprocess_audit_resets_stale_scan_and_triggers():
    audit = Audit(session_token="token", status=AuditStatus.SCANNING.value)
    audit.id = uuid.uuid4()
    db = MagicMock()

    with patch("admin.service.get_audit_by_id", return_value=audit):
        with patch("admin.service.trigger_verification") as mock_trigger:
            result = admin_reprocess_audit(db, audit.id)

    assert audit.status == AuditStatus.READY_FOR_SCAN.value
    db.commit.assert_called()
    mock_trigger.assert_called_once_with(db, audit)
    assert result["audit_id"] == audit.id
