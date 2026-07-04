from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from core.canonical_entities import CanonicalEntity
from verification.types import LeakFamily, Severity

if TYPE_CHECKING:
    from verification.context import CanonicalContext

EligibilityFn = Callable[["CanonicalContext"], tuple[bool, str | None]]


@dataclass(frozen=True)
class FieldRequirement:
    entity: CanonicalEntity
    field: str

    def key(self) -> tuple[str, str]:
        return (self.entity.value, self.field)


@dataclass
class RuleSpec:
    rule_id: str
    name: str
    category: str
    purpose: str
    required_fields: list[FieldRequirement] = field(default_factory=list)
    optional_fields: list[FieldRequirement] = field(default_factory=list)
    eligibility_conditions: EligibilityFn | None = None
    trigger_description: str = ""
    ignored_cases: str = ""
    severity_default: Severity = "medium"
    leak_family: LeakFamily = "operational"
    rule_version: str = "2.0.0"
    recommendation_template: str = ""

    def field(self, entity: CanonicalEntity, name: str, *, optional: bool = False) -> FieldRequirement:
        req = FieldRequirement(entity=entity, field=name)
        if optional:
            self.optional_fields.append(req)
        else:
            self.required_fields.append(req)
        return req


EligibilityStatus = Literal["runnable", "partial", "skipped"]
