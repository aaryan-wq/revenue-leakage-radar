import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.enums import UploadStatus
from models import Upload
from upload.cleanup import purge_audit_upload_files


@pytest.fixture
def temp_upload_dir(tmp_path):
    with patch("upload.cleanup.settings") as mock_settings:
        mock_settings.upload_dir = str(tmp_path)
        yield tmp_path


def test_purge_audit_upload_files_deletes_files_and_marks_purged(temp_upload_dir):
    audit_id = uuid.uuid4()
    audit_dir = temp_upload_dir / str(audit_id)
    audit_dir.mkdir(parents=True)
    file_path = audit_dir / "invoice_line_items_abc.csv"
    file_path.write_text("col\nval", encoding="utf-8")

    upload = Upload(
        audit_id=audit_id,
        file_type="invoice_line_items",
        original_filename="invoice_line_items.csv",
        storage_path=str(file_path),
        file_size=10,
        status=UploadStatus.UPLOADED.value,
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [upload]

    count = purge_audit_upload_files(db, audit_id)

    assert count == 1
    assert not file_path.exists()
    assert not audit_dir.exists()
    assert upload.status == UploadStatus.PURGED.value
    db.commit.assert_called_once()


def test_purge_skips_already_purged_uploads(temp_upload_dir):
    audit_id = uuid.uuid4()
    upload = Upload(
        audit_id=audit_id,
        file_type="invoice_line_items",
        original_filename="invoice_line_items.csv",
        storage_path=str(temp_upload_dir / "missing.csv"),
        file_size=10,
        status=UploadStatus.PURGED.value,
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [upload]

    count = purge_audit_upload_files(db, audit_id)

    assert count == 0
    db.commit.assert_called_once()
