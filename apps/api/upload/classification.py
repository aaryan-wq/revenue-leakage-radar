"""Bidirectional CSV file-type detection from filename and content."""

from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import polars as pl

from adapters.headers import map_header_to_canonical
from canonical.fields import CANONICAL_FIELDS, REQUIRED_CANONICAL_FIELDS
from core.enums import FILENAME_ALIASES, FILENAME_TO_FILE_TYPE, FileType

logger = logging.getLogger(__name__)

DetectionSource = Literal["filename", "content", "ai", "combined"]

CONFIDENCE_THRESHOLD = 0.7
FILENAME_HIGH_CONFIDENCE = 0.9
CONTENT_WEAK_THRESHOLD = 0.5
MIN_HEADER_SCORE = 4
MIN_HEADER_MARGIN = 2
REQUIRED_FIELD_WEIGHT = 3
OPTIONAL_FIELD_WEIGHT = 1

_NOISE_TOKENS = ("export", "data", "report", "dump", "backup", "extract")
_PLATFORM_PREFIXES = ("stripe", "chargebee", "maxio", "zuora", "salesforce", "hubspot")


@dataclass(frozen=True)
class FileTypeDetection:
    file_type: FileType
    source: DetectionSource
    confidence: float


def read_csv_headers_and_sample(
    content: bytes,
    sample_rows: int = 3,
) -> tuple[list[str], list[dict[str, str]]]:
    if not content.strip():
        return [], []

    try:
        df = pl.read_csv(
            io.BytesIO(content),
            n_rows=sample_rows,
            infer_schema_length=0,
        )
        headers = list(df.columns)
        rows = df.to_dicts()
        normalized_rows = [
            {k: str(v) if v is not None else "" for k, v in row.items()} for row in rows
        ]
        return headers, normalized_rows
    except Exception as exc:
        logger.debug("Failed to parse CSV headers from upload content: %s", exc)
        return [], []


def _normalize_filename_stem(filename: str) -> str:
    stem = Path(filename).stem.lower()
    stem = re.sub(r"[-_]?(20\d{2})([-_]\d{2})?([-_]\d{2})?$", "", stem)
    stem = re.sub(r"[-_]?\d{8}$", "", stem)

    for prefix in _PLATFORM_PREFIXES:
        stem = re.sub(rf"^{prefix}[-_]?", "", stem)

    for token in _NOISE_TOKENS:
        stem = re.sub(rf"[-_]?{token}[-_]?", "_", stem)

    stem = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    return stem


def classify_from_filename(filename: str) -> FileTypeDetection | None:
    stem = Path(filename).stem.lower()
    name = filename.lower()

    exact = FILENAME_TO_FILE_TYPE.get(stem) or FILENAME_TO_FILE_TYPE.get(name)
    if exact is not None:
        return FileTypeDetection(file_type=exact, source="filename", confidence=1.0)

    normalized = _normalize_filename_stem(filename)
    if normalized in FILENAME_TO_FILE_TYPE:
        file_type = FILENAME_TO_FILE_TYPE[normalized]
        return FileTypeDetection(file_type=file_type, source="filename", confidence=0.95)

    for token, file_type, confidence in FILENAME_ALIASES:
        if token in normalized or token in stem.replace("-", "_").replace(".", "_"):
            return FileTypeDetection(file_type=file_type, source="filename", confidence=confidence)

    tokens = set(normalized.split("_"))
    for token, file_type, confidence in FILENAME_ALIASES:
        if token in tokens:
            return FileTypeDetection(file_type=file_type, source="filename", confidence=confidence - 0.05)

    return None


def _score_headers_for_type(headers: list[str], file_type: FileType) -> int:
    if file_type == FileType.UNKNOWN:
        return 0

    required = set(REQUIRED_CANONICAL_FIELDS.get(file_type, []))
    optional = set(CANONICAL_FIELDS.get(file_type, [])) - required
    matched_required: set[str] = set()
    matched_optional: set[str] = set()

    for header in headers:
        canonical = map_header_to_canonical(header, file_type)
        if canonical is None:
            continue
        if canonical in required:
            matched_required.add(canonical)
        elif canonical in optional:
            matched_optional.add(canonical)

    return (
        len(matched_required) * REQUIRED_FIELD_WEIGHT
        + len(matched_optional) * OPTIONAL_FIELD_WEIGHT
    )


def _header_confidence(score: int, file_type: FileType) -> float:
    required = REQUIRED_CANONICAL_FIELDS.get(file_type, [])
    optional = [field for field in CANONICAL_FIELDS.get(file_type, []) if field not in required]
    max_score = len(required) * REQUIRED_FIELD_WEIGHT + len(optional) * OPTIONAL_FIELD_WEIGHT
    if max_score == 0:
        return 0.0
    return min(1.0, score / max_score)


def classify_from_headers(headers: list[str]) -> FileTypeDetection | None:
    if not headers:
        return None

    scores: dict[FileType, int] = {}
    for file_type in FileType:
        if file_type == FileType.UNKNOWN:
            continue
        score = _score_headers_for_type(headers, file_type)
        if score > 0:
            scores[file_type] = score

    if not scores:
        return None

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_type, best_score = ranked[0]
    runner_up_score = ranked[1][1] if len(ranked) > 1 else 0

    if best_score < MIN_HEADER_SCORE or (best_score - runner_up_score) < MIN_HEADER_MARGIN:
        return None

    return FileTypeDetection(
        file_type=best_type,
        source="content",
        confidence=_header_confidence(best_score, best_type),
    )


def _maybe_classify_with_ai(
    filename: str,
    headers: list[str],
    sample_rows: list[dict[str, str]],
) -> FileTypeDetection | None:
    from ai.file_type import classify_with_ai

    return classify_with_ai(filename, headers, sample_rows)


def resolve_file_type(
    filename: str,
    headers: list[str],
    sample_rows: list[dict[str, str]],
) -> FileTypeDetection:
    filename_result = classify_from_filename(filename)
    content_result = classify_from_headers(headers)

    if (
        filename_result is not None
        and content_result is not None
        and filename_result.file_type == content_result.file_type
    ):
        return FileTypeDetection(
            file_type=filename_result.file_type,
            source="combined",
            confidence=max(filename_result.confidence, content_result.confidence),
        )

    if (
        filename_result is not None
        and content_result is not None
        and filename_result.file_type != content_result.file_type
    ):
        if (
            filename_result.confidence >= FILENAME_HIGH_CONFIDENCE
            and content_result.confidence < CONTENT_WEAK_THRESHOLD
        ):
            return filename_result

        ai_result = _maybe_classify_with_ai(filename, headers, sample_rows)
        if ai_result is not None:
            return ai_result

        return content_result

    if filename_result is not None and content_result is None:
        if filename_result.confidence >= CONFIDENCE_THRESHOLD:
            return filename_result
        ai_result = _maybe_classify_with_ai(filename, headers, sample_rows)
        return ai_result or filename_result

    if content_result is not None and filename_result is None:
        if content_result.confidence >= CONFIDENCE_THRESHOLD:
            return content_result
        ai_result = _maybe_classify_with_ai(filename, headers, sample_rows)
        return ai_result or content_result

    ai_result = _maybe_classify_with_ai(filename, headers, sample_rows)
    if ai_result is not None:
        return ai_result

    if filename_result is not None:
        return filename_result
    if content_result is not None:
        return content_result

    return FileTypeDetection(file_type=FileType.UNKNOWN, source="filename", confidence=0.0)


def detect_file_type_from_upload(filename: str, content: bytes) -> FileTypeDetection:
    headers, sample_rows = read_csv_headers_and_sample(content)
    return resolve_file_type(filename, headers, sample_rows)
