from functools import lru_cache

from core.config import settings
from storage.backend import StorageBackend
from storage.local import LocalStorageBackend
from storage.r2 import R2StorageBackend


@lru_cache(maxsize=1)
def get_storage() -> StorageBackend:
    if settings.storage_backend == "r2":
        return R2StorageBackend(
            account_id=settings.r2_account_id,
            access_key_id=settings.r2_access_key_id,
            secret_access_key=settings.r2_secret_access_key,
            endpoint=settings.r2_endpoint,
            bucket_uploads=settings.r2_bucket_uploads,
            bucket_reports=settings.r2_bucket_reports,
        )
    return LocalStorageBackend(settings.upload_dir)


def upload_key(audit_id: str, filename: str) -> str:
    return f"uploads/{audit_id}/{filename}"


def report_export_key(report_id: str, filename: str) -> str:
    return f"reports/{report_id}/{filename}"
