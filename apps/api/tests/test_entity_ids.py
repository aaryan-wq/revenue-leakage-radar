import uuid
from decimal import Decimal
from unittest.mock import MagicMock

from models import Finding
from reports.entity_ids import EntityIdResolver, display_entity_ids, entity_refs_from_evidence
from reports.findings import build_primary_finding_lookup, serialize_finding


def test_entity_refs_from_evidence_extracts_native_ids():
    evidence = {
        "records": [
            {
                "field": "unit_price",
                "expected": "100",
                "actual": "80",
                "reference_ids": {
                    "customer_id": "acct_cust_00100",
                    "subscription_id": "sub_00100",
                },
            }
        ]
    }
    refs = entity_refs_from_evidence(evidence)
    assert refs["customer"] == "acct_cust_00100"
    assert refs["subscription"] == "sub_00100"


def test_serialize_finding_uses_external_entity_ids():
    customer_uuid = uuid.uuid4()
    subscription_uuid = uuid.uuid4()
    invoice_uuid = uuid.uuid4()

    finding = Finding(
        id=uuid.uuid4(),
        audit_id=uuid.uuid4(),
        rule_id="expired_discount",
        severity="high",
        confidence=Decimal("85"),
        customer_id=customer_uuid,
        subscription_id=subscription_uuid,
        invoice_id=invoice_uuid,
        estimated_monthly_loss=Decimal("100"),
        estimated_arr_loss=Decimal("1200"),
        evidence='{"records": []}',
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.all.side_effect = [
        [MagicMock(id=customer_uuid, external_customer_id="acct_cust_00100")],
        [MagicMock(id=subscription_uuid, external_subscription_id="sub_00100")],
        [MagicMock(id=invoice_uuid, external_invoice_id="inv_00100", invoice_number="INV-100")],
    ]

    resolver = EntityIdResolver.for_findings(db, [finding])
    payload = serialize_finding(finding, entity_resolver=resolver)

    assert payload["customer_id"] == "acct_cust_00100"
    assert payload["subscription_id"] == "sub_00100"
    assert payload["invoice_id"] == "inv_00100"


def test_serialize_secondary_finding_includes_primary_title():
    primary_id = uuid.uuid4()
    primary_ref = "primary-ref-abc"

    primary = Finding(
        id=primary_id,
        audit_id=uuid.uuid4(),
        rule_id="expired_discount",
        rule_name="Expired Discount Still Applied",
        severity="high",
        confidence=Decimal("90"),
        estimated_monthly_loss=Decimal("100"),
        estimated_arr_loss=Decimal("1200"),
        evidence='{"records": []}',
        attribution="primary",
        finding_ref=primary_ref,
    )
    secondary = Finding(
        id=uuid.uuid4(),
        audit_id=primary.audit_id,
        rule_id="grandfathered_pricing",
        rule_name="Grandfathered Pricing",
        severity="medium",
        confidence=Decimal("80"),
        estimated_monthly_loss=Decimal("80"),
        estimated_arr_loss=Decimal("960"),
        evidence='{"records": []}',
        attribution="secondary",
        primary_finding_ref=primary_ref,
        finding_ref="secondary-ref",
    )

    lookup = build_primary_finding_lookup([primary, secondary])
    payload = serialize_finding(secondary, primary_by_ref=lookup)

    assert payload["primary_finding_id"] == str(primary_id)
    assert payload["primary_finding_title"] == "Expired Discount Still Applied"


def test_display_entity_ids_falls_back_to_evidence():
    finding = Finding(
        id=uuid.uuid4(),
        audit_id=uuid.uuid4(),
        rule_id="expired_discount",
        severity="high",
        confidence=Decimal("85"),
        estimated_monthly_loss=Decimal("10"),
        estimated_arr_loss=Decimal("120"),
        evidence='{"records": [{"reference_ids": {"customer_id": "acct_cust_00100"}}]}',
    )
    evidence = {"records": [{"reference_ids": {"customer_id": "acct_cust_00100"}}]}
    customer_id, subscription_id, invoice_id = display_entity_ids(finding, evidence, None)
    assert customer_id == "acct_cust_00100"
    assert subscription_id is None
    assert invoice_id is None
