from pathlib import Path

import polars as pl

from core.enums import FileType


class CSVParseError(Exception):
    pass


def read_csv_file(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise CSVParseError(f"File not found: {path}")

    try:
        return pl.read_csv(path, infer_schema_length=1000, try_parse_dates=True)
    except Exception as exc:
        raise CSVParseError(f"Unable to parse CSV: {path.name}") from exc


def apply_column_mapping(df: pl.DataFrame, mapping: dict[str, str]) -> pl.DataFrame:
    if not mapping:
        return df

    rename_map = {source: target for source, target in mapping.items() if source in df.columns}
    if not rename_map:
        return df

    return df.rename(rename_map)


def load_uploaded_frames(
    uploads: list,
    column_mappings: dict[str, dict[str, str]],
) -> dict[FileType, pl.DataFrame]:
    frames: dict[FileType, pl.DataFrame] = {}

    for upload in uploads:
        file_type = FileType(upload.file_type)
        if file_type == FileType.UNKNOWN:
            continue

        path = Path(upload.storage_path)
        df = read_csv_file(path)
        mapping = column_mappings.get(file_type.value, {})
        frames[file_type] = apply_column_mapping(df, mapping)

    return frames
