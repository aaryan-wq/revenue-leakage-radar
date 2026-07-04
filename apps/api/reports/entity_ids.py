"""Resolve internal canonical UUIDs to native billing/CRM identifiers for display."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from models import Customer, Finding, Invoice, Subscription

_REFERENCE_KEY_TO_ENTITY = {
    "customer_id": "customer",
    "customer": "customer",
    "subscription_id": "subscription",
    "subscription": "subscription",
    "invoice_id": "invoice",
    "invoice": "invoice",
}


class EntityIdResolver:
    def __init__(self) -> None:
        self._customers: dict[uuid.UUID, str] = {}
        self._subscriptions: dict[uuid.UUID, str] = {}
        self._invoices: dict[uuid.UUID, str] = {}

    @classmethod
    def for_findings(cls, db: Session, findings: list[Finding]) -> EntityIdResolver:
        resolver = cls()
        customer_ids = {finding.customer_id for finding in findings if finding.customer_id}
        subscription_ids = {finding.subscription_id for finding in findings if finding.subscription_id}
        invoice_ids = {finding.invoice_id for finding in findings if finding.invoice_id}

        if customer_ids:
            rows = (
                db.query(Customer.id, Customer.external_customer_id)
                .filter(Customer.id.in_(customer_ids))
                .all()
            )
            resolver._customers = {row.id: row.external_customer_id for row in rows}

        if subscription_ids:
            rows = (
                db.query(Subscription.id, Subscription.external_subscription_id)
                .filter(Subscription.id.in_(subscription_ids))
                .all()
            )
            resolver._subscriptions = {row.id: row.external_subscription_id for row in rows}

        if invoice_ids:
            rows = (
                db.query(Invoice.id, Invoice.external_invoice_id, Invoice.invoice_number)
                .filter(Invoice.id.in_(invoice_ids))
                .all()
            )
            resolver._invoices = {
                row.id: row.external_invoice_id or row.invoice_number for row in rows
            }

        return resolver

    def customer_id(self, internal_id: uuid.UUID | None) -> str | None:
        if internal_id is None:
            return None
        return self._customers.get(internal_id, str(internal_id))

    def subscription_id(self, internal_id: uuid.UUID | None) -> str | None:
        if internal_id is None:
            return None
        return self._subscriptions.get(internal_id, str(internal_id))

    def invoice_id(self, internal_id: uuid.UUID | None) -> str | None:
        if internal_id is None:
            return None
        return self._invoices.get(internal_id, str(internal_id))


def entity_refs_from_evidence(evidence: dict[str, Any]) -> dict[str, str | None]:
    """Use native IDs embedded in evidence when entity FKs were not resolved."""
    found: dict[str, str | None] = {
        "customer": None,
        "subscription": None,
        "invoice": None,
    }
    for record in evidence.get("records", []):
        refs = record.get("reference_ids") or {}
        for key, value in refs.items():
            if not value:
                continue
            entity = _REFERENCE_KEY_TO_ENTITY.get(key)
            if entity and found[entity] is None:
                found[entity] = str(value)
    return found


def display_entity_ids(
    finding: Finding,
    evidence: dict[str, Any],
    resolver: EntityIdResolver | None,
) -> tuple[str | None, str | None, str | None]:
    fallback = entity_refs_from_evidence(evidence)
    if resolver is None:
        return (
            fallback["customer"],
            fallback["subscription"],
            fallback["invoice"],
        )
    customer_id = resolver.customer_id(finding.customer_id) or fallback["customer"]
    subscription_id = resolver.subscription_id(finding.subscription_id) or fallback["subscription"]
    invoice_id = resolver.invoice_id(finding.invoice_id) or fallback["invoice"]
    return customer_id, subscription_id, invoice_id
