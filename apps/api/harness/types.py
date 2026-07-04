"""Ground truth and company profile types for the verification harness."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class CompanyProfile:
    company_id: str
    name: str
    industry: str
    arr_target: Decimal
    customer_count: int
    product_count: int
    billing_platform: str
    crm_platform: str
    currency: str
    locale: str
    pricing_strategy: str
    seat_based: bool


@dataclass(frozen=True)
class GroundTruthFinding:
    """Expected finding recorded at injection time, never inferred post-hoc."""

    rule_id: str
    customer_id: str | None = None
    subscription_id: str | None = None
    invoice_id: str | None = None
    expected_monthly_leakage: Decimal = Decimal("0")
    expected_annual_leakage: Decimal = Decimal("0")
    expected_severity: str = "medium"
    expected_evidence: dict[str, Any] = field(default_factory=dict)
    is_negative: bool = False

    def match_key(self) -> tuple[str, str | None, str | None, str | None]:
        return (self.rule_id, self.customer_id, self.subscription_id, self.invoice_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "customer_id": self.customer_id,
            "subscription_id": self.subscription_id,
            "invoice_id": self.invoice_id,
            "expected_monthly_leakage": str(self.expected_monthly_leakage),
            "expected_annual_leakage": str(self.expected_annual_leakage),
            "expected_severity": self.expected_severity,
            "expected_evidence": self.expected_evidence,
            "is_negative": self.is_negative,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GroundTruthFinding:
        return cls(
            rule_id=data["rule_id"],
            customer_id=data.get("customer_id"),
            subscription_id=data.get("subscription_id"),
            invoice_id=data.get("invoice_id"),
            expected_monthly_leakage=Decimal(str(data.get("expected_monthly_leakage", "0"))),
            expected_annual_leakage=Decimal(str(data.get("expected_annual_leakage", "0"))),
            expected_severity=data.get("expected_severity", "medium"),
            expected_evidence=data.get("expected_evidence", {}),
            is_negative=bool(data.get("is_negative", False)),
        )


@dataclass
class GroundTruthDocument:
    profile: CompanyProfile
    findings: list[GroundTruthFinding]
    seed: int
    injected_rules: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": {
                "company_id": self.profile.company_id,
                "name": self.profile.name,
                "industry": self.profile.industry,
                "arr_target": str(self.profile.arr_target),
                "customer_count": self.profile.customer_count,
                "product_count": self.profile.product_count,
                "billing_platform": self.profile.billing_platform,
                "crm_platform": self.profile.crm_platform,
                "currency": self.profile.currency,
                "locale": self.profile.locale,
                "pricing_strategy": self.profile.pricing_strategy,
                "seat_based": self.profile.seat_based,
            },
            "seed": self.seed,
            "injected_rules": self.injected_rules,
            "findings": [f.to_dict() for f in self.findings],
        }
