import uuid

import pytest

from storage.factory import get_storage, upload_key
from storage.local import LocalStorageBackend


def test_local_storage_put_get_delete():
    backend = LocalStorageBackend("./test-uploads-tmp")
    key = upload_key(str(uuid.uuid4()), "subscriptions.csv")
    backend.put(key, b"a,b\n1,2", bucket="uploads")
    assert backend.exists(key, bucket="uploads")
    assert backend.get(key, bucket="uploads") == b"a,b\n1,2"
    backend.delete(key, bucket="uploads")
    assert not backend.exists(key, bucket="uploads")


def test_report_export_key_round_trip():
    backend = LocalStorageBackend("./test-uploads-tmp")
    report_id = str(uuid.uuid4())
    key = f"reports/{report_id}/report.pdf"
    backend.put(key, b"%PDF", bucket="reports")
    assert backend.get(key, bucket="reports") == b"%PDF"
