#!/usr/bin/env python3
"""End-to-end smoke test against a running API (staging or local)."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Install httpx: pip install httpx")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
GOLDEN_DIR = ROOT / "testdata" / "runs" / "run_991337" / "upload"
GOLDEN_FILES = [
    "customers.csv",
    "subscriptions.csv",
    "invoices.csv",
    "invoice_line_items.csv",
    "price_catalog.csv",
    "coupons.csv",
    "accounts.csv",
    "contracts.csv",
]


def wait_for_status(
    client: httpx.Client,
    audit_id: str,
    session_token: str,
    *,
    target_status: str,
    timeout_s: int,
) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        response = client.get(
            f"/audit/{audit_id}",
            headers={"X-Audit-Session": session_token},
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") == target_status:
            return payload
        time.sleep(2)
    raise TimeoutError(f"Audit {audit_id} did not reach status {target_status}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test audit pipeline against running API")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL for the API",
    )
    parser.add_argument("--timeout", type=int, default=600, help="Scan timeout in seconds")
    args = parser.parse_args()

    if not GOLDEN_DIR.exists():
        print(f"Golden dataset missing at {GOLDEN_DIR}")
        sys.exit(1)

    with httpx.Client(base_url=args.api_url.rstrip("/"), timeout=120.0) as client:
        health = client.get("/health")
        health.raise_for_status()
        print(f"✓ Health OK ({args.api_url})")

        create = client.post("/audit")
        create.raise_for_status()
        session = create.json()
        audit_id = session["audit_id"]
        session_token = session["session_token"]
        headers = {"X-Audit-Session": session_token}
        print(f"✓ Audit created {audit_id}")

        for filename in GOLDEN_FILES:
            file_path = GOLDEN_DIR / filename
            with file_path.open("rb") as handle:
                response = client.post(
                    f"/audit/{audit_id}/upload",
                    headers=headers,
                    files={"file": (filename, handle, "text/csv")},
                )
            response.raise_for_status()
            print(f"  uploaded {filename}")

        validate = client.post(f"/audit/{audit_id}/validate", headers=headers)
        validate.raise_for_status()
        print("✓ Validation started")

        wait_for_status(client, audit_id, session_token, target_status="ready_for_scan", timeout_s=120)
        print("✓ Ready for scan")

        scan = client.post(f"/audit/{audit_id}/scan", headers=headers)
        scan.raise_for_status()
        print("✓ Scan started")

        completed = wait_for_status(
            client,
            audit_id,
            session_token,
            target_status="completed",
            timeout_s=args.timeout,
        )
        scan_report = completed.get("scan_report") or {}
        finding_count = scan_report.get("finding_count", 0)
        recoverable_arr = scan_report.get("recoverable_arr", "0")
        print(f"✓ Scan complete: {finding_count} findings, ARR {recoverable_arr}")

        if finding_count < 20:
            print(f"FAIL: expected at least 20 findings, got {finding_count}")
            sys.exit(1)

        summary = client.get(f"/summary/{audit_id}", headers=headers)
        summary.raise_for_status()
        summary_data = summary.json()
        print(f"✓ Summary recoverable ARR: {summary_data.get('recoverable_arr')}")

    print("\nSmoke test passed.")


if __name__ == "__main__":
    main()
