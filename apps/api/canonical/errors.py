from dataclasses import dataclass, field
from typing import Any


@dataclass
class RowError:
    file_type: str
    row_index: int
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_type": self.file_type,
            "row_index": self.row_index,
            "message": self.message,
        }


@dataclass
class TransformResult:
    row_errors: list[RowError] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_errors": [e.to_dict() for e in self.row_errors],
            "counts": self.counts,
        }
