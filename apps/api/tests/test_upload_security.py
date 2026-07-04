import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile as StarletteUploadFile

from upload.service import validate_csv_file


def _upload_file(name: str) -> StarletteUploadFile:
    return StarletteUploadFile(filename=name, file=iter([b"a,b\n1,2\n"]))


def test_validate_csv_rejects_path_traversal():
    with pytest.raises(HTTPException) as exc:
        validate_csv_file(_upload_file("../../subscriptions.csv"))
    assert exc.value.status_code == 400
    assert "Invalid filename" in exc.value.detail


def test_validate_csv_rejects_backslash_path():
    with pytest.raises(HTTPException) as exc:
        validate_csv_file(_upload_file("..\\subscriptions.csv"))
    assert exc.value.status_code == 400


def test_validate_csv_rejects_null_byte_in_filename():
    with pytest.raises(HTTPException) as exc:
        validate_csv_file(_upload_file("subscriptions.csv\x00.exe"))
    assert exc.value.status_code == 400


def test_validate_csv_accepts_standard_filename():
    validate_csv_file(_upload_file("subscriptions.csv"))
