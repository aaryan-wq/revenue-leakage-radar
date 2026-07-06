#!/usr/bin/env python3
"""Stress-test CSV ingestion with fuzzed synthetic exports across billing platforms."""

from __future__ import annotations

import argparse
import random
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT_FIXTURES = ROOT / "testdata" / "exports"
sys.path.insert(0, str(ROOT / "apps" / "api"))

from harness.company_generator import generate_company
from harness.csv_fuzzer import CsvFuzzConfig

PLATFORMS = ["stripe", "chargebee", "maxio", "zuora", "paddle", "recurly", "hubspot", "salesforce"]
EXPORT_PLATFORMS = ["chargebee", "zuora"]


def run_iteration(seed: int, customer_count: int, platform: str) -> dict[str, float | str | int]:
    rng = random.Random(seed)
    company = generate_company(seed=seed, customer_count=customer_count, verification_mode=True)
    fuzz = CsvFuzzConfig(
        platform=platform,
        header_style=rng.choice(["random", "snake", "camel", "title"]),
        shuffle_columns=True,
        add_blank_rows=rng.random() < 0.2,
        add_extra_columns=True,
        drop_optional_columns=rng.random() < 0.3,
        whitespace_pad=rng.random() < 0.2,
        date_format=rng.choice([None, "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]),
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        start = time.perf_counter()
        paths = company.export_csvs(tmp_path, rng, fuzz)
        export_ms = (time.perf_counter() - start) * 1000

        from adapters.headers import build_column_mappings
        from core.enums import FileType
        from harness.context_loader import _load_rows_from_dir
        from validation.parser import apply_column_mapping

        start = time.perf_counter()
        file_headers: dict[FileType, list[str]] = {}
        for file_key, file_path in paths.items():
            import csv

            with file_path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                headers = next(reader, [])
            try:
                file_type = FileType(file_key)
            except ValueError:
                continue
            file_headers[file_type] = headers

        mappings = build_column_mappings(file_headers)
        rows_by_entity: dict[str, list[dict[str, str]]] = {}
        for file_key, file_path in paths.items():
            try:
                file_type = FileType(file_key)
            except ValueError:
                continue
            import polars as pl

            df = pl.read_csv(file_path, infer_schema_length=1000)
            mapped = apply_column_mapping(df, mappings.get(file_key, {}))
            rows_by_entity[file_key] = [dict(row) for row in mapped.iter_rows(named=True)]

        from harness.context_loader import build_context_from_state

        ctx, _ = build_context_from_state(rows_by_entity)
        parse_ms = (time.perf_counter() - start) * 1000

    return {
        "seed": seed,
        "platform": platform,
        "customers": customer_count,
        "files": len(paths),
        "export_ms": export_ms,
        "parse_ms": parse_ms,
        "frames": len(paths),
        "subscriptions": len(ctx.subscriptions),
    }


def validate_export_fixture(platform: str) -> dict[str, float | str | int]:
    fixture_dir = EXPORT_FIXTURES / platform
    if not fixture_dir.exists():
        raise FileNotFoundError(f"Export fixture directory missing: {fixture_dir}")

    from adapters.headers import build_column_mappings
    from core.enums import FileType
    from validation.parser import apply_column_mapping

    start = time.perf_counter()
    file_headers: dict[FileType, list[str]] = {}
    csv_files = sorted(fixture_dir.glob("*.csv"))
    for file_path in csv_files:
        import csv

        with file_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            headers = next(reader, [])
        stem = file_path.stem
        alias = {
            "accounts": FileType.CRM_ACCOUNTS,
            "invoice_line_items": FileType.INVOICE_LINE_ITEMS,
            "price_catalog": FileType.PRICE_CATALOG,
        }.get(stem, FileType(stem) if stem in {ft.value for ft in FileType} else None)
        if alias is None:
            continue
        file_headers[alias] = headers

    mappings = build_column_mappings(file_headers)
    mapped_count = 0
    for file_path in csv_files:
        stem = file_path.stem
        try:
            file_type = FileType(stem)
        except ValueError:
            if stem == "accounts":
                file_type = FileType.CRM_ACCOUNTS
            else:
                continue
        import polars as pl

        df = pl.read_csv(file_path, infer_schema_length=1000)
        apply_column_mapping(df, mappings.get(file_type.value, {}))
        mapped_count += 1

    parse_ms = (time.perf_counter() - start) * 1000

    return {
        "platform": platform,
        "files": len(csv_files),
        "parse_ms": parse_ms,
        "mapped_files": mapped_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="CSV ingestion chaos stress test")
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--customers", type=int, default=100)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--include-export-fixtures",
        action="store_true",
        help="Also validate static Chargebee/Zuora export fixtures",
    )
    args = parser.parse_args()

    failures = 0
    print(f"{'Seed':>6} {'Platform':>12} {'Files':>6} {'Export':>10} {'Parse':>10}")
    print("-" * 52)

    if args.include_export_fixtures:
        print("Export fixture validation:")
        for platform in EXPORT_PLATFORMS:
            try:
                row = validate_export_fixture(platform)
                print(
                    f"{'—':>6} {row['platform']:>12} {row['files']:>6} "
                    f"{'—':>10} {row['parse_ms']:>8.0f}ms"
                )
            except Exception as exc:
                failures += 1
                print(f"{'—':>6} {platform:>12} FAILED: {exc}")
        print("-" * 52)

    for index in range(args.iterations):
        seed = args.seed + index
        platform = PLATFORMS[index % len(PLATFORMS)]
        try:
            row = run_iteration(seed, args.customers, platform)
            print(
                f"{row['seed']:>6} {row['platform']:>12} {row['files']:>6} "
                f"{row['export_ms']:>8.0f}ms {row['parse_ms']:>8.0f}ms"
            )
        except Exception as exc:
            failures += 1
            print(f"{seed:>6} {platform:>12} FAILED: {exc}")

    if failures:
        print(f"\n{failures} iteration(s) failed.")
        sys.exit(1)
    print(f"\nAll {args.iterations} chaos iterations passed.")


if __name__ == "__main__":
    main()
