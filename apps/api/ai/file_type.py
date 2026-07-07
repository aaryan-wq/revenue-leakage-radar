import json
import logging

from ai.prompts.file_type import FILE_TYPE_SYSTEM_PROMPT
from ai.provider import AIProviderError, call_openai_json
from core.enums import FileType
from upload.classification import FileTypeDetection

logger = logging.getLogger(__name__)


def _build_user_prompt(
    filename: str,
    headers: list[str],
    sample_rows: list[dict[str, str]],
) -> str:
    return (
        f"Filename: {filename}\n"
        f"Headers: {headers}\n"
        f"Sample rows: {json.dumps(sample_rows[:3])}"
    )


def classify_with_ai(
    filename: str,
    headers: list[str],
    sample_rows: list[dict[str, str]],
) -> FileTypeDetection | None:
    if not headers:
        return None

    try:
        user_prompt = _build_user_prompt(filename, headers, sample_rows)
        result = call_openai_json(FILE_TYPE_SYSTEM_PROMPT, user_prompt)
        file_type_str = result.get("file_type", "unknown")
        if file_type_str not in FileType._value2member_map_:
            return None
        file_type = FileType(file_type_str)
        if file_type == FileType.UNKNOWN:
            return None
        confidence = float(result.get("confidence", 0.8))
        confidence = max(0.0, min(1.0, confidence))
        return FileTypeDetection(file_type=file_type, source="ai", confidence=confidence)
    except (AIProviderError, ValueError, TypeError) as exc:
        logger.info("AI file type classification failed: %s", exc)
        return None
