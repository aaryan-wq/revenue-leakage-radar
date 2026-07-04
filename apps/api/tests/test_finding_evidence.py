import json
import uuid
from decimal import Decimal

from verification.outputs import rule_finding_to_orm
from verification.types import LeakageComputation, RuleFinding


def test_rule_finding_evidence_serializes_decimal_leakage_computation() -> None:
    finding = RuleFinding(
        rule_id="invoice_price_mismatch",
        rule_name="Invoice Price Mismatch",
        title="Invoice price mismatch",
        severity="high",
        confidence=Decimal("92"),
        estimated_monthly_loss=Decimal("125.50"),
        estimated_arr_loss=Decimal("1506.00"),
        recommendation="Review invoice line pricing.",
        leakage_computation=LeakageComputation(
            semantics="recurring_run_rate",
            unit_expected=Decimal("99.00"),
            unit_actual=Decimal("49.00"),
            quantity=1,
            billing_interval="month",
            monthly_loss=Decimal("50.00"),
            annual_loss=Decimal("600.00"),
            formula="(expected - actual) * quantity",
        ),
    )

    orm = rule_finding_to_orm(uuid.uuid4(), finding)
    evidence = json.loads(orm.evidence)

    assert evidence["leakage_computation"]["unit_expected"] == "99.00"
    assert evidence["leakage_computation"]["annual_loss"] == "600.00"
