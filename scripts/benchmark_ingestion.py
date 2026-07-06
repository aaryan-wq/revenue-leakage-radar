#!/usr/bin/env python3
"""Benchmark full canonical ingestion (CSV frames → DB) at increasing scales."""

from __future__ import annotations

import argparse
import secrets
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api"))

import polars as pl

from canonical.transformer import run_canonical_transform
from core.enums import AuditStatus, FileType
from database.session import SessionLocal
from harness.company_generator import generate_company
from ingestion.types import IngestionContext
from models import Audit


def _frames_from_company(company, *, customer_count: int) -> dict[FileType, pl.DataFrame]:
    rows = company.rows()
    frames: dict[FileType, pl.DataFrame] = {}
    mapping = {
        FileType.CUSTOMERS: "customers",
        FileType.SUBSCRIPTIONS: "subscriptions",
        FileType.INVOICES: "invoices",
        FileType.INVOICE_LINE_ITEMS: "invoice_line_items",
        FileType.COUPONS: "coupons",
        FileType.PRICE_CATALOG: "price_catalog",
        FileType.CRM_ACCOUNTS: "crm_accounts",
        FileType.CRM_CONTRACTS: "crm_contracts",
    }
    for file_type, key in mapping.items():
        data = rows.get(key, [])
        if data:
            frames[file_type] = pl.DataFrame(data)
    return frames


def benchmark_ingestion(customer_count: int, seed: int) -> dict[str, float]:
    db = SessionLocal()
    audit = Audit(
        session_token=secrets.token_urlsafe(32),
        status=AuditStatus.READY_FOR_SCAN.value,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    start = time.perf_counter()
    company = generate_company(seed=seed, customer_count=customer_count, verification_mode=True)
    gen_ms = (time.perf_counter() - start) * 1000

    frames = _frames_from_company(company, customer_count=customer_count)
    ctx = IngestionContext(
        audit_id=str(audit.id),
        frames=frames,
        uploaded_file_types=set(frames.keys()),
    )

    start = time.perf_counter()
    result = run_canonical_transform(db, audit, ctx)
    ingest_ms = (time.perf_counter() - start) * 1000

    db.delete(audit)
    if audit.company_id:
        from models import Company

        company_row = db.query(Company).filter(Company.id == audit.company_id).first()
        if company_row:
            db.delete(company_row)
    db.commit()
    db.close()

    return {
        "customers": float(customer_count),
        "entities": float(sum(result.counts.values())),
        "generate_ms": gen_ms,
        "ingest_ms": ingest_ms,
        "total_ms": gen_ms + ingest_ms,
        "row_errors": float(len(result.row_errors)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark canonical ingestion performance")
    parser.add_argument(
        "--sizes",
        nargs="*",
        type=int,
        default=[100, 500, 1000, 5000],
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--max-ingest-ms",
        type=int,
        default=0,
        help="Fail if ingestion exceeds this threshold at largest size (0 = no gate)",
    )
    args = parser.parse_args()

    print(f"{'Customers':>10} {'Entities':>10} {'Generate':>12} {'Ingest':>12} {'Total':>12}")
    print("-" * 60)

    largest_ingest = 0.0
    for size in args.sizes:
        row = benchmark_ingestion(size, args.seed + size)
        largest_ingest = max(largest_ingest, row["ingest_ms"])
        print(
            f"{int(row['customers']):>10} "
            f"{int(row['entities']):>10} "
            f"{row['generate_ms']:>10.0f}ms "
            f"{row['ingest_ms']:>10.0f}ms "
            f"{row['total_ms']:>10.0f}ms"
        )
        if row["row_errors"] > 0:
            print(f"  WARNING: {int(row['row_errors'])} row errors")

    if args.max_ingest_ms > 0 and largest_ingest > args.max_ingest_ms:
        print(
            f"\nFAIL: largest ingestion {largest_ingest:.0f}ms exceeds "
            f"threshold {args.max_ingest_ms}ms"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
