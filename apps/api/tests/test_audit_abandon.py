import uuid
from unittest.mock import MagicMock, patch

import pytest

from audit.service import abandon_audit_session, can_abandon_audit
from core.enums import AuditStatus
from models import Audit, Report


def test_can_abandon_in_progress_audit():
    audit = Audit(session_token="token", status=AuditStatus.UPLOADING.value)
    can_abandon, reason = can_abandon_audit(audit)
    assert can_abandon is True
    assert reason is None


def test_cannot_abandon_completed_audit():
    audit = Audit(session_token="token", status=AuditStatus.COMPLETED.value)
    can_abandon, reason = can_abandon_audit(audit)
    assert can_abandon is False
    assert reason is None


def test_cannot_abandon_purchased_report():
    audit = Audit(session_token="token", status=AuditStatus.READY_FOR_SCAN.value)
    audit.report = Report(purchased=True, recoverable_arr=0, finding_count=0)
    can_abandon, reason = can_abandon_audit(audit)
    assert can_abandon is False
    assert reason is not None


@patch("canonical.transformer.clear_canonical_data")
@patch("upload.cleanup.purge_audit_upload_files_by_audit")
def test_abandon_audit_session_deletes_audit(mock_purge, mock_clear_canonical):
    audit = Audit(session_token="token", status=AuditStatus.VALIDATING.value)
    audit.id = uuid.uuid4()
    audit.company_id = uuid.uuid4()
    db = MagicMock()
    db.query.return_value.filter.return_value.count.return_value = 0

    deleted = abandon_audit_session(db, audit)

    assert deleted is True
    mock_purge.assert_called_once_with(db, audit)
    db.delete.assert_called()
    mock_clear_canonical.assert_called_once_with(db, audit.company_id)
    db.commit.assert_called_once()


@patch("upload.cleanup.purge_audit_upload_files_by_audit")
def test_abandon_completed_audit_is_noop(mock_purge):
    audit = Audit(session_token="token", status=AuditStatus.COMPLETED.value)
    db = MagicMock()

    deleted = abandon_audit_session(db, audit)

    assert deleted is False
    mock_purge.assert_not_called()
    db.delete.assert_not_called()
