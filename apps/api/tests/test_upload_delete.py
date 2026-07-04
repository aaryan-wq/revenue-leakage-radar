import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from core.enums import AuditStatus, FileType, UploadStatus
from models import Audit, Upload
from upload.service import delete_upload


def _audit_with_uploads(*uploads: Upload) -> Audit:
    audit = Audit(
        id=uuid.uuid4(),
        session_token="test-token",
        status=AuditStatus.UPLOADING.value,
    )
    audit.uploads = list(uploads)
    audit.available_entities = ["subscription", "price"]
    audit.data_tier = "tier_1"
    return audit


def test_delete_upload_removes_file_and_recomputes_coverage(tmp_path, monkeypatch):
    monkeypatch.setattr("upload.service.settings.upload_dir", str(tmp_path))

    audit_id = uuid.uuid4()
    upload_id = uuid.uuid4()
    other_id = uuid.uuid4()
    storage_path = tmp_path / str(audit_id) / "subscriptions.csv"
    storage_path.parent.mkdir(parents=True)
    storage_path.write_text("subscription_id,customer_id,status\nsub_1,c1,active")

    upload = Upload(
        id=upload_id,
        audit_id=audit_id,
        file_type=FileType.SUBSCRIPTIONS.value,
        original_filename="subscriptions.csv",
        storage_path=str(storage_path),
        file_size=100,
        status=UploadStatus.UPLOADED.value,
    )
    other = Upload(
        id=other_id,
        audit_id=audit_id,
        file_type=FileType.PRICE_CATALOG.value,
        original_filename="price_catalog.csv",
        storage_path=str(tmp_path / str(audit_id) / "price_catalog.csv"),
        file_size=100,
        status=UploadStatus.UPLOADED.value,
    )
    audit = _audit_with_uploads(upload, other)

    db = MagicMock()

    def query_upload(*_args, **_kwargs):
        query = MagicMock()

        def first():
            for item in audit.uploads:
                if item.id == upload_id:
                    return item
            return None

        query.filter.return_value.first = first
        return query

    db.query.side_effect = query_upload

    def delete_side_effect(obj):
        audit.uploads.remove(obj)

    db.delete.side_effect = delete_side_effect

    delete_upload(db, audit, upload_id)

    assert not storage_path.exists()
    assert upload not in audit.uploads
    assert audit.available_entities == ["price"]
    assert audit.uploaded_file_types == ["price_catalog"]
    assert audit.data_tier == "tier_0"
    db.commit.assert_called_once()


def test_delete_upload_not_found():
    audit = _audit_with_uploads()
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        delete_upload(db, audit, uuid.uuid4())

    assert exc.value.status_code == 404
