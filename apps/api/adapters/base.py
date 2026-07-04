"""Platform adapter contract for CSV → Canonical Entity Model translation."""

from dataclasses import dataclass, field
from typing import Protocol

import polars as pl

from core.canonical_entities import CanonicalEntity
from core.enums import FileType, Platform
from models import Upload


@dataclass
class AdapterOutput:
    platform: Platform
    column_mappings: dict[str, dict[str, str]] = field(default_factory=dict)
    detected_entities: set[CanonicalEntity] = field(default_factory=set)


class PlatformAdapter(Protocol):
    def detect_platform(self, file_headers: dict[FileType, list[str]]) -> Platform: ...

    def map_columns(self, file_headers: dict[FileType, list[str]]) -> dict[str, dict[str, str]]: ...

    def classify_upload(self, filename: str, headers: list[str] | None = None) -> FileType: ...
