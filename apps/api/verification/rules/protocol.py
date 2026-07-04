from __future__ import annotations

from typing import Protocol

from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.types import RuleResult


class RuleModule(Protocol):
    spec: RuleSpec

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]: ...
