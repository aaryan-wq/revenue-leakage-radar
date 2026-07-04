import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from audit.service import delete_user_audit
from core.enums import AuditStatus
from models import Audit


def test_delete_user_audit_removes_audit():
    audit = Audit(session_token="token", status=AuditStatus.COMPLETED.value, clerk_user_id="user_1")
    audit.id = uuid.uuid4()
    db = MagicMock()

    with patch("upload.cleanup.purge_audit_upload_files_by_audit") as mock_purge:
        delete_user_audit(db, audit, "user_1")

    mock_purge.assert_called_once_with(db, audit)
    db.delete.assert_called_once_with(audit)
    db.commit.assert_called_once()


def test_delete_user_audit_rejects_wrong_user():
    audit = Audit(session_token="token", status=AuditStatus.COMPLETED.value, clerk_user_id="user_1")
    db = MagicMock()

    with pytest.raises(PermissionError):
        delete_user_audit(db, audit, "user_2")


def test_delete_user_audit_rejects_in_progress():
    audit = Audit(session_token="token", status=AuditStatus.SCANNING.value, clerk_user_id="user_1")
    db = MagicMock()

    with pytest.raises(ValueError, match="in progress"):
        delete_user_audit(db, audit, "user_1")
