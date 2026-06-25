import json
import logging
from pathlib import Path

import polars as pl

from ai.fallback import build_fallback_mappings
from ai.prompts.mapping import MAPPING_SYSTEM_PROMPT
from ai.provider import AIProviderError, call_openai_json
from canonical.fields import CANONICAL_FIELDS
from core.enums import FileType, Platform
from models import Upload

logger = logging.getLogger(__name__)

SAMPLE_ROWS = 5


def _read_csv_sample(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    df = pl.read_csv(path, n_rows=SAMPLE_ROWS, infer_schema_length=0)
    headers = df.columns
    rows = df.to_dicts()
    return headers, [{k: str(v) if v is not None else "" for k, v in row.items()} for row in rows]


def _build_user_prompt(file_data: dict[FileType, dict]) -> str:
    sections = []
    for file_type, data in file_data.items():
        canonical_list = CANONICAL_FIELDS.get(file_type, [])
        sections.append(
            f"File type: {file_type.value}\n"
            f"Canonical fields: {', '.join(canonical_list)}\n"
            f"Headers: {data['headers']}\n"
            f"Sample rows: {json.dumps(data['rows'][:SAMPLE_ROWS])}"
        )
    return "\n\n".join(sections)


def detect_and_map_uploads(uploads: list[Upload]) -> tuple[Platform, dict[str, dict[str, str]]]:
    file_data: dict[FileType, dict] = {}
    file_headers: dict[FileType, list[str]] = {}

    for upload in uploads:
        file_type = FileType(upload.file_type)
        if file_type == FileType.UNKNOWN:
            continue
        path = Path(upload.storage_path)
        if not path.exists():
            continue
        headers, rows = _read_csv_sample(path)
        file_headers[file_type] = headers
        file_data[file_type] = {"headers": headers, "rows": rows}

    if not file_headers:
        return Platform.GENERIC, {}

    try:
        user_prompt = _build_user_prompt(file_data)
        result = call_openai_json(MAPPING_SYSTEM_PROMPT, user_prompt)
        platform_str = result.get("platform", "generic")
        platform = Platform(platform_str) if platform_str in Platform._value2member_map_ else Platform.GENERIC
        mappings = result.get("mappings", {})
        if mappings:
            return platform, mappings
    except (AIProviderError, ValueError) as exc:
        logger.info("AI mapping failed, using fallback: %s", exc)

    platform_str, mappings = build_fallback_mappings(file_headers)
    platform = Platform(platform_str) if platform_str in Platform._value2member_map_ else Platform.GENERIC
    return platform, mappings
