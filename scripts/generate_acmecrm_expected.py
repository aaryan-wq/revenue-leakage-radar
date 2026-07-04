#!/usr/bin/env python3
"""Generate AcmeCRM expected.json golden bounds from the corrected verification engine."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import sys

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "apps" / "api"))

from compare_acmecrm_leakage import build_context
from verification.attribution import attribute_findings, sum_primary_recoverable_arr
from verification.registry import get_all_rules

DATA = ROOT / "testdata" / "acmecrm"


def main() -> None:
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    ctx = build_context()

    findings = []
    for rule in get_all_rules():
        if rule.evaluate:
            findings.extend(rule.evaluate(ctx))

    attributed = attribute_findings(findings)
    portfolio_primary = sum_primary_recoverable_arr(attributed)

    scenarios: dict[str, dict] = {}
    for scenario_name, scenario in manifest["injected_scenarios"].items():
        external_sub_ids = set(scenario["subscription_ids"])
        scenario_primary = Decimal("0")
        matched_rules: set[str] = set()
        for finding in attributed:
            if finding.attribution != "primary":
                continue
            if not finding.subscription_id:
                continue
            ext_sub = next(
                (
                    sub.external_subscription_id
                    for sub in ctx.subscriptions
                    if str(sub.id) == str(finding.subscription_id)
                ),
                None,
            )
            if ext_sub in external_sub_ids:
                scenario_primary += finding.estimated_arr_loss
                matched_rules.add(finding.rule_id)

        margin = max(Decimal("1"), (scenario_primary * Decimal("0.02")).quantize(Decimal("0.01")))
        scenarios[scenario_name] = {
            "rule_id": scenario["rule_id"],
            "subscription_ids": scenario["subscription_ids"],
            "primary_arr_min": str((scenario_primary - margin).quantize(Decimal("0.01"))),
            "primary_arr_max": str((scenario_primary + margin).quantize(Decimal("0.01"))),
            "matched_rules": sorted(matched_rules),
        }

    portfolio_margin = max(Decimal("1000"), (portfolio_primary * Decimal("0.02")).quantize(Decimal("0.01")))
    payload = {
        "scenarios": scenarios,
        "portfolio": {
            "primary_recoverable_arr_min": str((portfolio_primary - portfolio_margin).quantize(Decimal("0.01"))),
            "primary_recoverable_arr_max": str((portfolio_primary + portfolio_margin).quantize(Decimal("0.01"))),
            "max_finding_count": len(attributed),
            "primary_finding_count": sum(1 for f in attributed if f.attribution == "primary"),
        },
    }
    out = DATA / "expected.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps(payload["portfolio"], indent=2))


if __name__ == "__main__":
    main()
