"""Hand-crafted minimal billing scenarios with explicit, auditable ground truth."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from harness.types import CompanyProfile, GroundTruthDocument, GroundTruthFinding


@dataclass(frozen=True)
class MinimalFixture:
    rows: dict[str, list[dict]]
    ground_truth: GroundTruthDocument


def _profile(fixture_id: str, name: str, *, customer_count: int = 1) -> CompanyProfile:
    return CompanyProfile(
        company_id=f"co_{fixture_id}",
        name=name,
        industry="SaaS",
        arr_target=Decimal("120000"),
        customer_count=customer_count,
        product_count=1,
        billing_platform="stripe",
        crm_platform="none",
        currency="USD",
        locale="en-US",
        pricing_strategy="flat",
        seat_based=False,
    )


def build_normal_company() -> MinimalFixture:
    """Fixture 01, consistent billing with zero leakage."""
    rows = {
        "customers": [{"customer_id": "cust_001", "name": "Acme Corp", "crm_id": ""}],
        "subscriptions": [
            {
                "subscription_id": "sub_001",
                "customer_id": "cust_001",
                "product_id": "prod_starter_mo",
                "plan": "Starter",
                "quantity": 10,
                "billing_interval": "monthly",
                "price": "100.00",
                "currency": "USD",
                "start_date": "2024-08-01",
                "renewal_date": "2025-08-01",
                "status": "active",
                "coupon_id": "",
            }
        ],
        "price_catalog": [
            {
                "product_id": "prod_starter_mo",
                "sku": "SKU-STRT",
                "version": "v1",
                "effective_date": "2024-01-01",
                "list_price": "100.00",
                "currency": "USD",
                "billing_interval": "monthly",
            }
        ],
        "invoices": [
            {
                "invoice_id": "inv_001",
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "invoice_number": "INV-001",
                "invoice_date": "2024-09-01",
                "period_start": "2024-09-01",
                "period_end": "2024-10-01",
                "subtotal": "1000.00",
                "discount": "0.00",
                "total": "1000.00",
                "currency": "USD",
                "credit_amount": "0.00",
            }
        ],
        "invoice_line_items": [
            {
                "line_item_id": "li_001",
                "invoice_id": "inv_001",
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "product_id": "prod_starter_mo",
                "sku": "SKU-STRT",
                "quantity": 10,
                "unit_price": "100.00",
                "extended_price": "1000.00",
                "billing_interval": "monthly",
                "line_item_date": "2024-09-01",
                "currency": "USD",
                "is_manual_override": "false",
            }
        ],
        "coupons": [],
        "crm_accounts": [],
        "crm_contracts": [],
    }
    doc = GroundTruthDocument(
        profile=_profile("01", "Normal Company"),
        findings=[],
        seed=0,
        injected_rules=[],
    )
    return MinimalFixture(rows=rows, ground_truth=doc)


def build_expired_discount() -> MinimalFixture:
    """Fixture 02, coupon expired; $250 MRR / $3,000 ARR leakage."""
    rows = {
        "customers": [{"customer_id": "cust_001", "name": "Beta Inc", "crm_id": ""}],
        "subscriptions": [
            {
                "subscription_id": "sub_001",
                "customer_id": "cust_001",
                "product_id": "prod_pro_mo",
                "plan": "Pro",
                "quantity": 1,
                "billing_interval": "monthly",
                "price": "250.00",
                "currency": "USD",
                "start_date": "2024-01-01",
                "renewal_date": "2025-01-01",
                "status": "active",
                "coupon_id": "LAUNCH50",
            }
        ],
        "coupons": [
            {
                "coupon_id": "cpn_launch50",
                "code": "LAUNCH50",
                "discount_type": "percent",
                "discount_value": "50",
                "expires_at": "2024-03-31",
                "active": "true",
            }
        ],
        "price_catalog": [
            {
                "product_id": "prod_pro_mo",
                "sku": "SKU-PRO",
                "version": "v1",
                "effective_date": "2024-01-01",
                "list_price": "500.00",
                "currency": "USD",
                "billing_interval": "monthly",
            }
        ],
        "invoices": [
            {
                "invoice_id": "inv_001",
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "invoice_number": "INV-001",
                "invoice_date": "2024-02-01",
                "period_start": "2024-02-01",
                "period_end": "2024-03-01",
                "subtotal": "250.00",
                "discount": "0.00",
                "total": "250.00",
                "currency": "USD",
                "credit_amount": "0.00",
            },
            {
                "invoice_id": "inv_002",
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "invoice_number": "INV-002",
                "invoice_date": "2024-06-01",
                "period_start": "2024-06-01",
                "period_end": "2024-07-01",
                "subtotal": "250.00",
                "discount": "125.00",
                "total": "125.00",
                "currency": "USD",
                "credit_amount": "0.00",
            },
        ],
        "invoice_line_items": [
            {
                "line_item_id": "li_001",
                "invoice_id": "inv_001",
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "product_id": "prod_pro_mo",
                "sku": "SKU-PRO",
                "quantity": 1,
                "unit_price": "250.00",
                "extended_price": "250.00",
                "billing_interval": "monthly",
                "line_item_date": "2024-02-01",
                "currency": "USD",
                "is_manual_override": "false",
            },
            {
                "line_item_id": "li_002",
                "invoice_id": "inv_002",
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "product_id": "prod_pro_mo",
                "sku": "SKU-PRO",
                "quantity": 1,
                "unit_price": "250.00",
                "extended_price": "250.00",
                "billing_interval": "monthly",
                "line_item_date": "2024-06-01",
                "currency": "USD",
                "is_manual_override": "false",
            },
        ],
        "crm_accounts": [],
        "crm_contracts": [],
    }
    finding = GroundTruthFinding(
        rule_id="expired_discount",
        customer_id="cust_001",
        subscription_id="sub_001",
        invoice_id="inv_002",
        expected_monthly_leakage=Decimal("250"),
        expected_annual_leakage=Decimal("3000"),
        expected_severity="high",
        expected_evidence={
            "catalog_list_price": "500.00",
            "subscription_price": "250.00",
            "coupon": "LAUNCH50",
            "coupon_expires": "2024-03-31",
            "evidence_invoice_date": "2024-06-01",
            "calculation": "(500.00 - 250.00) × 1 seat = $250/mo → $3,000 ARR",
        },
    )
    doc = GroundTruthDocument(
        profile=_profile("02", "Expired Discount Co"),
        findings=[finding],
        seed=0,
        injected_rules=["expired_discount"],
    )
    return MinimalFixture(rows=rows, ground_truth=doc)


def build_legacy_pricing() -> MinimalFixture:
    """Fixture 03, subscription below post-increase catalog; $600 MRR / $7,200 ARR."""
    rows = {
        "customers": [{"customer_id": "cust_001", "name": "Legacy Corp", "crm_id": ""}],
        "subscriptions": [
            {
                "subscription_id": "sub_001",
                "customer_id": "cust_001",
                "product_id": "prod_growth_mo",
                "plan": "Growth",
                "quantity": 6,
                "billing_interval": "monthly",
                "price": "500.00",
                "currency": "USD",
                "start_date": "2022-06-01",
                "renewal_date": "2025-06-01",
                "status": "active",
                "coupon_id": "",
            }
        ],
        "price_catalog": [
            {
                "product_id": "prod_growth_mo",
                "sku": "SKU-GRW",
                "version": "v2",
                "effective_date": "2024-07-01",
                "list_price": "600.00",
                "currency": "USD",
                "billing_interval": "monthly",
            },
        ],
        "invoices": [
            {
                "invoice_id": "inv_001",
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "invoice_number": "INV-001",
                "invoice_date": "2024-08-01",
                "period_start": "2024-08-01",
                "period_end": "2024-09-01",
                "subtotal": "3000.00",
                "discount": "0.00",
                "total": "3000.00",
                "currency": "USD",
                "credit_amount": "0.00",
            }
        ],
        "invoice_line_items": [
            {
                "line_item_id": "li_001",
                "invoice_id": "inv_001",
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "product_id": "prod_growth_mo",
                "sku": "SKU-GRW",
                "quantity": 6,
                "unit_price": "500.00",
                "extended_price": "3000.00",
                "billing_interval": "monthly",
                "line_item_date": "2024-08-01",
                "currency": "USD",
                "is_manual_override": "false",
            }
        ],
        "coupons": [],
        "crm_accounts": [],
        "crm_contracts": [],
    }
    finding = GroundTruthFinding(
        rule_id="legacy_pricing",
        customer_id="cust_001",
        subscription_id="sub_001",
        expected_monthly_leakage=Decimal("600"),
        expected_annual_leakage=Decimal("7200"),
        expected_severity="medium",
        expected_evidence={
            "catalog_v2_price": "600.00",
            "subscription_price": "500.00",
            "quantity": "6",
            "calculation": "(600.00 - 500.00) × 6 seats = $600/mo → $7,200 ARR",
        },
    )
    doc = GroundTruthDocument(
        profile=_profile("03", "Legacy Pricing Co"),
        findings=[finding],
        seed=0,
        injected_rules=["legacy_pricing"],
    )
    return MinimalFixture(rows=rows, ground_truth=doc)


def build_negative_all_rules() -> MinimalFixture:
    """Clean company, every rule must NOT fire."""
    base = build_normal_company()
    from harness.injections import ALL_RULE_IDS

    negatives = [
        GroundTruthFinding(rule_id=rule_id, is_negative=True) for rule_id in ALL_RULE_IDS
    ]
    doc = GroundTruthDocument(
        profile=_profile("27", "Negative Control Co"),
        findings=negatives,
        seed=0,
        injected_rules=[],
    )
    return MinimalFixture(rows=base.rows, ground_truth=doc)


def build_edge_zero_quantity() -> MinimalFixture:
    """Zero-quantity subscription should not produce pricing leakage."""
    base = build_normal_company()
    rows = {**base.rows}
    rows["subscriptions"] = [{**base.rows["subscriptions"][0], "quantity": 0}]
    rows["invoice_line_items"] = [{**base.rows["invoice_line_items"][0], "quantity": 0, "extended_price": "0.00"}]
    rows["invoices"] = [{**base.rows["invoices"][0], "subtotal": "0.00", "total": "0.00"}]
    doc = GroundTruthDocument(
        profile=_profile("28", "Zero Quantity Co"),
        findings=[],
        seed=0,
        injected_rules=[],
    )
    return MinimalFixture(rows=rows, ground_truth=doc)


def build_edge_free_plan() -> MinimalFixture:
    """Free plan with zero price, no leakage."""
    rows = {
        "customers": [{"customer_id": "cust_001", "name": "Free Tier Co", "crm_id": ""}],
        "subscriptions": [
            {
                "subscription_id": "sub_001",
                "customer_id": "cust_001",
                "product_id": "prod_free_mo",
                "plan": "Free",
                "quantity": 1,
                "billing_interval": "monthly",
                "price": "0.00",
                "currency": "USD",
                "start_date": "2024-06-01",
                "renewal_date": "2025-06-01",
                "status": "active",
                "coupon_id": "",
            }
        ],
        "price_catalog": [
            {
                "product_id": "prod_free_mo",
                "sku": "SKU-FREE",
                "version": "v1",
                "effective_date": "2024-01-01",
                "list_price": "0.00",
                "currency": "USD",
                "billing_interval": "monthly",
            }
        ],
        "invoices": [],
        "invoice_line_items": [],
        "coupons": [],
        "crm_accounts": [],
        "crm_contracts": [],
    }
    doc = GroundTruthDocument(
        profile=_profile("29", "Free Plan Co"),
        findings=[],
        seed=0,
        injected_rules=[],
    )
    return MinimalFixture(rows=rows, ground_truth=doc)


def build_edge_cancelled_clean() -> MinimalFixture:
    """Cancelled subscription with no post-cancel invoices."""
    rows = {
        "customers": [{"customer_id": "cust_001", "name": "Cancelled Co", "crm_id": ""}],
        "subscriptions": [
            {
                "subscription_id": "sub_001",
                "customer_id": "cust_001",
                "product_id": "prod_starter_mo",
                "plan": "Starter",
                "quantity": 5,
                "billing_interval": "monthly",
                "price": "100.00",
                "currency": "USD",
                "start_date": "2024-01-01",
                "renewal_date": "2024-06-01",
                "status": "cancelled",
                "coupon_id": "",
            }
        ],
        "price_catalog": [
            {
                "product_id": "prod_starter_mo",
                "sku": "SKU-STRT",
                "version": "v1",
                "effective_date": "2024-01-01",
                "list_price": "100.00",
                "currency": "USD",
                "billing_interval": "monthly",
            }
        ],
        "invoices": [
            {
                "invoice_id": "inv_001",
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "invoice_number": "INV-001",
                "invoice_date": "2024-05-01",
                "period_start": "2024-05-01",
                "period_end": "2024-06-01",
                "subtotal": "500.00",
                "discount": "0.00",
                "total": "500.00",
                "currency": "USD",
                "credit_amount": "0.00",
            }
        ],
        "invoice_line_items": [
            {
                "line_item_id": "li_001",
                "invoice_id": "inv_001",
                "customer_id": "cust_001",
                "subscription_id": "sub_001",
                "product_id": "prod_starter_mo",
                "sku": "SKU-STRT",
                "quantity": 5,
                "unit_price": "100.00",
                "extended_price": "500.00",
                "billing_interval": "monthly",
                "line_item_date": "2024-05-01",
                "currency": "USD",
                "is_manual_override": "false",
            }
        ],
        "coupons": [],
        "crm_accounts": [],
        "crm_contracts": [],
    }
    doc = GroundTruthDocument(
        profile=_profile("30", "Cancelled Clean Co"),
        findings=[
            GroundTruthFinding(rule_id="cancelled_subscription_still_billing", is_negative=True),
        ],
        seed=0,
        injected_rules=[],
    )
    return MinimalFixture(rows=rows, ground_truth=doc)


def build_edge_orphaned_line_item() -> MinimalFixture:
    """Line item referencing a missing invoice parent."""
    base = build_normal_company()
    rows = {**base.rows}
    rows["invoice_line_items"] = list(rows["invoice_line_items"]) + [
        {
            "line_item_id": "li_orphan",
            "invoice_id": "00000000-0000-4000-8000-000000000099",
            "customer_id": "cust_001",
            "subscription_id": "",
            "product_id": "prod_starter_mo",
            "sku": "SKU-STRT",
            "quantity": 1,
            "unit_price": "100.00",
            "extended_price": "100.00",
            "billing_interval": "monthly",
            "line_item_date": "2024-10-01",
            "currency": "USD",
            "is_manual_override": "false",
        }
    ]
    doc = GroundTruthDocument(
        profile=_profile("31", "Orphaned Line Item Co"),
        findings=[
            GroundTruthFinding(
                rule_id="orphaned_records",
                customer_id="cust_001",
                expected_monthly_leakage=Decimal("0"),
                expected_annual_leakage=Decimal("0"),
                expected_severity="low",
            )
        ],
        seed=0,
        injected_rules=["orphaned_records"],
    )
    return MinimalFixture(rows=rows, ground_truth=doc)


MINIMAL_BUILDERS: dict[str, callable] = {
    "01_normal_company": build_normal_company,
    "02_expired_discount": build_expired_discount,
    "03_legacy_pricing": build_legacy_pricing,
    "27_negative_all_rules": build_negative_all_rules,
    "28_edge_zero_quantity": build_edge_zero_quantity,
    "29_edge_free_plan": build_edge_free_plan,
    "30_edge_cancelled_clean": build_edge_cancelled_clean,
    "31_edge_orphaned_line_item": build_edge_orphaned_line_item,
}
