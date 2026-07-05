import io
from pathlib import Path

import polars as pl

from storage.factory import get_storage


def storage_exists(storage_path: str) -> bool:
    storage = get_storage()
    if Path(storage_path).is_absolute() and Path(storage_path).exists():
        return True
    return storage.exists(storage_path, bucket="uploads")


def read_storage_bytes(storage_path: str) -> bytes:
    path = Path(storage_path)
    if path.is_absolute() and path.exists():
        return path.read_bytes()
    return get_storage().get(storage_path, bucket="uploads")


def read_csv_from_storage(storage_path: str, **kwargs) -> pl.DataFrame:
    content = read_storage_bytes(storage_path)
    return pl.read_csv(io.BytesIO(content), **kwargs)
