"""Backward-compatible re-exports, vendor logic lives in adapters/."""

from adapters.headers import (
    HEADER_SYNONYMS,
    build_column_mappings,
    map_header_to_canonical,
    normalize_header,
)
from adapters.registry import PLATFORM_HEADER_HINTS, detect_platform_from_headers


def detect_platform_fallback(file_samples: dict) -> str:
    return detect_platform_from_headers(file_samples).value


def build_fallback_mappings(file_headers: dict) -> tuple[str, dict[str, dict[str, str]]]:
    platform = detect_platform_from_headers(file_headers)
    mappings = build_column_mappings(file_headers)
    return platform.value, mappings
