"""Verification engine package.

Pipeline imports are deferred to avoid a circular import with coverage/registry.
Import from verification.engine.pipeline, .registry, or .runner directly.
"""

from verification.engine.registry import get_all_rules, get_rule_module
from verification.engine.runner import run_engine

__all__ = [
    "get_all_rules",
    "get_rule_module",
    "run_engine",
]
