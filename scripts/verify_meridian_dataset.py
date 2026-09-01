#!/usr/bin/env python3
"""Run verification engine on Meridian Platform CSV fixtures."""

from __future__ import annotations

import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api"))

from harness.context_loader import load_context_from_csv_dir
from harness.engine_runner import run_all_rules
from verification.attribution import attribute_findings, sum_primary_recoverable_arr, sum_secondary_excluded_arr

DATA_DIR = ROOT / "testdata" / "meridian_platform"


def main() -> None:
    ctx, _id_maps = load_context_from_csv_dir(DATA_DIR)
    result = run_all_rules(ctx)

    if result.errors:
        print("Engine errors:")
        for error in result.errors:
            print(f"  - {error}")

    findings = result.findings
    attributed = attribute_findings(findings)
    primary_arr = sum_primary_recoverable_arr(attributed)
    secondary_arr = sum_secondary_excluded_arr(attributed)
    raw_arr = sum((f.estimated_arr_loss for f in findings), Decimal("0"))

    by_rule: dict[str, dict[str, Decimal | int]] = defaultdict(lambda: {"count": 0, "arr": Decimal("0")})
    for finding in findings:
        by_rule[finding.rule_id]["count"] += 1
        by_rule[finding.rule_id]["arr"] += finding.estimated_arr_loss

    unique_subs = len({f.subscription_id for f in findings if f.subscription_id})

    print("Meridian Platform CSV audit results")
    print("=" * 60)
    print(f"Dataset: {DATA_DIR}")
    print(f"Customers loaded: {len(ctx.customers)}")
    print(f"Subscriptions loaded: {len(ctx.subscriptions)}")
    print(f"Invoices loaded: {len(ctx.invoices)}")
    print(f"Line items loaded: {len(ctx.line_items)}")
    print(f"CRM contracts loaded: {len(ctx.crm_contracts)}")
    print()
    print("Recoverable leakage (forward-looking ARR):")
    print(f"  Total findings: {len(findings)}")
    print(f"  Unique subscriptions flagged: {unique_subs}")
    print(f"  Raw sum ARR (overlapping): ${raw_arr:,.2f}")
    print(f"  Primary recoverable ARR (deduped): ${primary_arr:,.2f}")
    print(f"  Secondary excluded ARR: ${secondary_arr:,.2f}")
    if ctx.subscriptions:
        pct = (primary_arr / Decimal("27000000")) * 100
        print(f"  Primary as pct of $27M ARR: {pct:.2f}%")
    print()
    print("Top rules by recoverable ARR:")
    for rule_id, stats in sorted(by_rule.items(), key=lambda item: -item[1]["arr"])[:15]:
        if stats["arr"] > 0:
            print(f"  {rule_id}: {stats['count']} findings, ${stats['arr']:,.2f}")
    print()
    print("Sample findings (top 10 by ARR):")
    top = sorted(findings, key=lambda f: f.estimated_arr_loss, reverse=True)[:10]
    for finding in top:
        print(
            f"  {finding.rule_id} | sub={finding.subscription_id or 'n/a'} | "
            f"${finding.estimated_arr_loss:,.2f}/yr | conf={finding.confidence:.2f}"
        )


if __name__ == "__main__":
    main()
