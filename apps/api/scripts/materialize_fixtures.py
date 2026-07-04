#!/usr/bin/env python3
"""Materialize verification fixtures to tests/verification_fixtures/."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harness.fixture_catalog import FIXTURE_CATALOG
from harness.fixture_runner import materialize_all_fixtures


def main() -> int:
    paths = materialize_all_fixtures()
    print(f"Materialized {len(paths)} fixtures to tests/verification_fixtures/")
    for path in paths:
        print(f"  • {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
