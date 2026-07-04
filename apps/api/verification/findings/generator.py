from __future__ import annotations

import hashlib
import uuid
from decimal import Decimal

from verification.calculator.financial import normalize_interval
from verification.findings.evidence import build_evidence, trace_evidence_from_calculation
from verification.types import (
    LeakageComputation,
    RuleFinding,
    RuleResult,
    RuleScope,
)
from verification.eligibility.schema import RuleSpec


RULE_LEAK_FAMILIES: dict[str, str] = {
    "legacy_pricing": "subscription_pricing_gap",
    "price_catalog_mismatch": "subscription_pricing_gap",
    "grandfathered_pricing": "subscription_pricing_gap",
    "missing_scheduled_increase": "subscription_pricing_gap",
    "renewal_price_drift": "renewal_event",
    "manual_price_override": "invoice_execution",
    "incorrect_seat_price": "usage_monetization",
    "incorrect_addon_price": "subscription_pricing_gap",
    "expired_discount": "discount_integrity",
    "discount_stacking": "discount_integrity",
    "duplicate_discount": "discount_integrity",
    "permanent_promotional_discount": "discount_integrity",
    "excessive_discount": "discount_integrity",
    "discount_wrong_product": "discount_integrity",
    "invoice_price_mismatch": "invoice_execution",
    "duplicate_subscription": "usage_monetization",
    "billing_frequency_mismatch": "invoice_execution",
    "active_subscription_not_billing": "usage_monetization",
    "cancelled_subscription_still_billing": "invoice_execution",
    "missing_expected_invoice": "invoice_execution",
    "credit_leakage": "operational",
    "duplicate_credit": "operational",
    "duplicate_customer": "operational",
    "currency_mismatch": "operational",
    "orphaned_records": "operational",
}

RULE_PRIORITY: dict[str, int] = {
    "invoice_price_mismatch": 100,
    "price_catalog_mismatch": 90,
    "missing_scheduled_increase": 80,
    "legacy_pricing": 60,
    "grandfathered_pricing": 50,
    "expired_discount": 100,
    "discount_stacking": 90,
    "duplicate_discount": 85,
    "manual_price_override": 100,
    "billing_frequency_mismatch": 70,
    "renewal_price_drift": 80,
    "incorrect_seat_price": 100,
    "duplicate_subscription": 90,
    "currency_mismatch": 100,
    "credit_leakage": 90,
}


def deterministic_finding_ref(
    audit_id: uuid.UUID | str,
    rule_id: str,
    scope: RuleScope,
    trace_hash: str,
) -> str:
    scope_key = "|".join(
        value or ""
        for value in (
            scope.customer_id,
            scope.subscription_id,
            scope.invoice_id,
            scope.product_id,
        )
    )
    raw = f"{audit_id}:{rule_id}:{scope_key}:{trace_hash}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _leakage_computation_from_trace(result: RuleResult, interval: str = "monthly") -> LeakageComputation:
    trace = result.calculation
    unit_expected = result.expected_value or Decimal("0")
    unit_actual = result.actual_value or Decimal("0")
    quantity = 1
    for step in trace.steps:
        if step.step_id == "quantity":
            quantity = int(step.value)
    formula_steps = " → ".join(step.label for step in trace.steps)
    return LeakageComputation(
        semantics=trace.semantics if trace.semantics in ("recurring_run_rate", "per_period", "one_time") else "recurring_run_rate",
        unit_expected=unit_expected,
        unit_actual=unit_actual,
        quantity=quantity,
        billing_interval=normalize_interval(interval),
        monthly_loss=trace.result_monthly,
        annual_loss=trace.result_annual,
        formula=formula_steps,
    )


class FindingGenerator:
    @staticmethod
    def from_rule_result(
        spec: RuleSpec,
        result: RuleResult,
        *,
        audit_id: uuid.UUID | str,
        billing_interval: str | None = "monthly",
    ) -> RuleFinding:
        evidence_inputs = list(result.evidence_fields)
        evidence = build_evidence(evidence_inputs)
        for record in trace_evidence_from_calculation(result.calculation):
            if record.field not in {item.field for item in evidence}:
                evidence.append(record)

        finding_ref = deterministic_finding_ref(
            audit_id,
            spec.rule_id,
            result.scope,
            result.calculation.trace_hash_input(),
        )

        return RuleFinding(
            rule_id=spec.rule_id,
            rule_name=spec.name,
            title=spec.name,
            severity=result.severity,
            confidence=result.confidence,
            status="open",
            customer_id=result.scope.customer_id,
            subscription_id=result.scope.subscription_id,
            invoice_id=result.scope.invoice_id,
            product_id=result.scope.product_id,
            expected_value=result.expected_value,
            actual_value=result.actual_value,
            delta=result.difference,
            estimated_monthly_loss=result.calculation.result_monthly,
            estimated_arr_loss=result.calculation.result_annual,
            recommendation=result.recommendation or spec.recommendation_template or spec.purpose,
            evidence=evidence,
            calculation_trace=result.calculation,
            leak_family=RULE_LEAK_FAMILIES.get(spec.rule_id, spec.leak_family),
            leakage_computation=_leakage_computation_from_trace(result, billing_interval or "monthly"),
            rule_version=spec.rule_version,
            finding_ref=finding_ref,
            attribution="primary",
        )
