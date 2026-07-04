"""Mutable canonical row store for synthetic company generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from harness.types import CompanyProfile, GroundTruthFinding


@dataclass
class CompanyState:
    profile: CompanyProfile
    anchor_date: date | None = None
    customers: list[dict[str, Any]] = field(default_factory=list)
    subscriptions: list[dict[str, Any]] = field(default_factory=list)
    invoices: list[dict[str, Any]] = field(default_factory=list)
    line_items: list[dict[str, Any]] = field(default_factory=list)
    coupons: list[dict[str, Any]] = field(default_factory=list)
    price_catalog: list[dict[str, Any]] = field(default_factory=list)
    crm_accounts: list[dict[str, Any]] = field(default_factory=list)
    crm_contracts: list[dict[str, Any]] = field(default_factory=list)
    ground_truth: list[GroundTruthFinding] = field(default_factory=list)

    def subscription_by_id(self, subscription_id: str) -> dict[str, Any] | None:
        return next((s for s in self.subscriptions if s["subscription_id"] == subscription_id), None)

    def customer_by_id(self, customer_id: str) -> dict[str, Any] | None:
        return next((c for c in self.customers if c["customer_id"] == customer_id), None)

    def invoices_for_subscription(self, subscription_id: str) -> list[dict[str, Any]]:
        return [i for i in self.invoices if i.get("subscription_id") == subscription_id]

    def line_items_for_invoice(self, invoice_id: str) -> list[dict[str, Any]]:
        return [li for li in self.line_items if li.get("invoice_id") == invoice_id]

    def catalog_for_product(
        self,
        product_id: str,
        as_of: date | None = None,
    ) -> dict[str, Any] | None:
        ref = as_of or date.today()
        matches = [p for p in self.price_catalog if p["product_id"] == product_id]
        if not matches:
            return None
        valid = [
            p
            for p in matches
            if not p.get("effective_date") or date.fromisoformat(p["effective_date"]) <= ref
        ]
        pool = valid or matches
        return max(pool, key=lambda p: p.get("effective_date") or "0000-01-01")

    def latest_catalog(self, product_id: str) -> dict[str, Any] | None:
        matches = [p for p in self.price_catalog if p["product_id"] == product_id]
        if not matches:
            return None
        return max(matches, key=lambda p: p.get("effective_date") or "0000-01-01")

    def append_ground_truth(self, finding: GroundTruthFinding) -> None:
        self.ground_truth.append(finding)
