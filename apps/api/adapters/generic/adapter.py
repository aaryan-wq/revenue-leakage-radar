"""Generic CSV adapter, filename-based classification and header mapping."""

from pathlib import Path

from adapters.base import AdapterOutput
from adapters.headers import build_column_mappings
from core.canonical_entities import SOURCE_FILE_TYPE_TO_ENTITIES, entities_from_uploaded_files
from core.enums import FILENAME_TO_FILE_TYPE, FileType, Platform
from models import Upload


class GenericAdapter:
    def detect_platform(self, file_headers: dict[FileType, list[str]]) -> Platform:
        return Platform.GENERIC

    def map_columns(self, file_headers: dict[FileType, list[str]]) -> dict[str, dict[str, str]]:
        return build_column_mappings(file_headers)

    def classify_upload(self, filename: str, headers: list[str] | None = None) -> FileType:
        stem = Path(filename).stem.lower()
        name = filename.lower()
        return FILENAME_TO_FILE_TYPE.get(stem, FILENAME_TO_FILE_TYPE.get(name, FileType.UNKNOWN))


def map_uploads(uploads: list[Upload]) -> AdapterOutput:
    file_headers: dict[FileType, list[str]] = {}
    for upload in uploads:
        file_type = FileType(upload.file_type)
        if file_type == FileType.UNKNOWN:
            continue
        from storage.reader import read_csv_from_storage, storage_exists

        if not storage_exists(upload.storage_path):
            continue
        df = read_csv_from_storage(upload.storage_path, n_rows=0, infer_schema_length=0)
        file_headers[file_type] = df.columns

    uploaded_types = set(file_headers.keys())
    return AdapterOutput(
        platform=Platform.GENERIC,
        column_mappings=build_column_mappings(file_headers),
        detected_entities=entities_from_uploaded_files(uploaded_types),
    )
