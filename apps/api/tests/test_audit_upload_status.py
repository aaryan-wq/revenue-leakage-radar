import uuid
from unittest.mock import MagicMock

from audit.service import get_missing_required_file_types, get_uploaded_file_types, has_billing_upload
from core.enums import FileType, UploadStatus
from models import Audit, Upload


def _audit_with_uploads(*uploads: Upload) -> Audit:
    audit = Audit(
        id=uuid.uuid4(),
        session_token="test-token",
        status="ready_for_scan",
    )
    audit.uploads = list(uploads)
    return audit


def test_purged_uploads_count_toward_billing_upload():
    audit = _audit_with_uploads(
        Upload(
            audit_id=uuid.uuid4(),
            file_type=FileType.SUBSCRIPTIONS.value,
            original_filename="subscriptions.csv",
            storage_path="/tmp/subscriptions.csv",
            file_size=100,
            status=UploadStatus.PURGED.value,
        ),
        Upload(
            audit_id=uuid.uuid4(),
            file_type=FileType.PRICE_CATALOG.value,
            original_filename="price_catalog.csv",
            storage_path="/tmp/pc.csv",
            file_size=100,
            status=UploadStatus.PURGED.value,
        ),
    )

    assert get_uploaded_file_types(audit) == {
        FileType.SUBSCRIPTIONS,
        FileType.PRICE_CATALOG,
    }
    assert get_missing_required_file_types(audit) == []
    assert has_billing_upload(audit)


def test_failed_uploads_do_not_count_toward_billing_upload():
    audit = _audit_with_uploads(
        Upload(
            audit_id=uuid.uuid4(),
            file_type=FileType.INVOICE_LINE_ITEMS.value,
            original_filename="invoice_line_items.csv",
            storage_path="/tmp/li.csv",
            file_size=100,
            status=UploadStatus.FAILED.value,
        ),
    )

    assert FileType.INVOICE_LINE_ITEMS not in get_uploaded_file_types(audit)
    assert not has_billing_upload(audit)
