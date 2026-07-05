import uuid
from unittest.mock import MagicMock

import pytest

from core.enums import UploadStatus
from models import Upload
from storage.factory import upload_key
from storage.local import LocalStorageBackend
from upload.cleanup import purge_audit_upload_files


@pytest.fixture
def temp_storage(tmp_path, monkeypatch):
    backend = LocalStorageBackend(str(tmp_path))
    monkeypatch.setattr("upload.cleanup.get_storage", lambda: backend)
    monkeypatch.setattr("storage.reader.get_storage", lambda: backend)
    return backend, tmp_path


def test_purge_audit_upload_files_deletes_files_and_marks_purged(temp_storage):
    backend, tmp_path = temp_storage
    audit_id = uuid.uuid4()
    object_key = upload_key(str(audit_id), "invoice_line_items_abc.csv")
    backend.put(object_key, b"col\nval", bucket="uploads")

    upload = Upload(
        audit_id=audit_id,
        file_type="invoice_line_items",
        original_filename="invoice_line_items.csv",
        storage_path=object_key,
        file_size=10,
        status=UploadStatus.UPLOADED.value,
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [upload]

    count = purge_audit_upload_files(db, audit_id)

    assert count == 1
    assert not backend.exists(object_key, bucket="uploads")
    assert upload.status == UploadStatus.PURGED.value
    db.commit.assert_called_once()


def test_purge_skips_already_purged_uploads(temp_storage):
    audit_id = uuid.uuid4()
    upload = Upload(
        audit_id=audit_id,
        file_type="invoice_line_items",
        original_filename="invoice_line_items.csv",
        storage_path=upload_key(str(audit_id), "missing.csv"),
        file_size=10,
        status=UploadStatus.PURGED.value,
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [upload]

    count = purge_audit_upload_files(db, audit_id)

    assert count == 0
    db.commit.assert_called_once()
