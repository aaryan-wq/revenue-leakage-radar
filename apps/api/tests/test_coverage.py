from core.canonical_entities import CanonicalEntity
from core.enums import FileType
from verification.coverage import analyze_coverage, resolve_rule_availability
from verification.registry import get_all_rules


def test_analyze_coverage_with_rich_billing_data():
    entities = {
        CanonicalEntity.CUSTOMER,
        CanonicalEntity.SUBSCRIPTION,
        CanonicalEntity.PRICE,
        CanonicalEntity.INVOICE,
        CanonicalEntity.INVOICE_LINE_ITEM,
        CanonicalEntity.CONTRACT,
    }
    uploaded = {
        FileType.CUSTOMERS,
        FileType.SUBSCRIPTIONS,
        FileType.PRICE_CATALOG,
        FileType.INVOICES,
        FileType.INVOICE_LINE_ITEMS,
        FileType.CRM_CONTRACTS,
    }

    result = analyze_coverage(
        available_entities=entities,
        uploaded_file_types=uploaded,
        has_credit_data=False,
    )

    assert result["rules_total"] == len(get_all_rules())
    assert result["rules_available"] > 0
    assert len(result["available_rules"]) == result["rules_available"]
    assert "Customers" in result["billing_data_received"]
    assert result["estimated_confidence"] > 0
    assert any(item["category"] == "pricing" for item in result["category_scores"])
    assert any(item["category"] == "overall" for item in result["category_scores"])


def test_analyze_coverage_marks_credit_rule_unavailable_without_credit_data():
    entities = {
        CanonicalEntity.INVOICE,
        CanonicalEntity.INVOICE_LINE_ITEM,
    }

    result = analyze_coverage(
        available_entities=entities,
        uploaded_file_types={FileType.INVOICES},
        has_credit_data=False,
    )

    credit_rule = next(rule for rule in result["unavailable_rules"] if rule["name"] == "Credit Leakage")
    assert credit_rule["reason"] == "Missing credit data"
    credits_score = next(item for item in result["category_scores"] if item["category"] == "credits")
    assert credits_score["score"] == 0


def test_analyze_coverage_unlock_hints_suggest_missing_coupons():
    entities = {
        CanonicalEntity.CUSTOMER,
        CanonicalEntity.SUBSCRIPTION,
        CanonicalEntity.INVOICE,
        CanonicalEntity.PRICE,
    }

    result = analyze_coverage(
        available_entities=entities,
        uploaded_file_types={
            FileType.CUSTOMERS,
            FileType.SUBSCRIPTIONS,
            FileType.INVOICES,
            FileType.PRICE_CATALOG,
        },
    )

    coupon_hint = next((hint for hint in result["unlock_hints"] if hint["file_type"] == "coupons"), None)
    assert coupon_hint is not None
    assert coupon_hint["rules_unlocked"] >= 1


def test_preview_mode_includes_credit_and_manual_rules_with_full_billing_data():
    entities = {
        CanonicalEntity.CUSTOMER,
        CanonicalEntity.SUBSCRIPTION,
        CanonicalEntity.PRICE,
        CanonicalEntity.INVOICE,
        CanonicalEntity.INVOICE_LINE_ITEM,
        CanonicalEntity.COUPON,
        CanonicalEntity.ACCOUNT,
        CanonicalEntity.CONTRACT,
    }
    uploaded = {
        FileType.CUSTOMERS,
        FileType.SUBSCRIPTIONS,
        FileType.PRICE_CATALOG,
        FileType.INVOICES,
        FileType.INVOICE_LINE_ITEMS,
        FileType.COUPONS,
        FileType.CRM_ACCOUNTS,
        FileType.CRM_CONTRACTS,
    }

    result = analyze_coverage(
        available_entities=entities,
        uploaded_file_types=uploaded,
        has_credit_data=False,
        preview_mode=True,
    )

    assert result["rules_available"] == len(get_all_rules())
    assert result["rules_total"] == len(get_all_rules())


def test_resolve_rule_availability_partial_when_optimal_entities_missing():
    rule = next(rule for rule in get_all_rules() if rule.rule_id == "renewal_price_drift")
    availability = resolve_rule_availability(
        rule,
        {CanonicalEntity.SUBSCRIPTION, CanonicalEntity.INVOICE},
    )
    assert availability.status == "partial"
