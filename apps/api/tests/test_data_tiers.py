from core.canonical_entities import CanonicalEntity, MINIMUM_BILLING_ENTITIES
from core.data_tiers import (
    TIER_1_RECOMMENDED_ENTITIES,
    get_audit_data_tier_from_entities,
    has_minimum_billing_entities,
    missing_recommended_entities,
    missing_tier_0_entities,
    tier_0_complete,
    tier_0_entities_complete,
)
from core.enums import DataTier, FileType


def test_minimum_billing_entities():
    assert CanonicalEntity.CUSTOMER in MINIMUM_BILLING_ENTITIES
    assert CanonicalEntity.INVOICE_LINE_ITEM in MINIMUM_BILLING_ENTITIES


def test_tier_1_recommended_entities():
    assert CanonicalEntity.CUSTOMER in TIER_1_RECOMMENDED_ENTITIES
    assert CanonicalEntity.PRICE in TIER_1_RECOMMENDED_ENTITIES


def test_get_audit_data_tier_progression():
    minimal = {CanonicalEntity.SUBSCRIPTION}
    assert get_audit_data_tier_from_entities(minimal) == DataTier.TIER_0

    tier1 = minimal | TIER_1_RECOMMENDED_ENTITIES
    assert get_audit_data_tier_from_entities(tier1) == DataTier.TIER_1

    tier2 = tier1 | {CanonicalEntity.COUPON}
    assert get_audit_data_tier_from_entities(tier2) == DataTier.TIER_2_PLUS


def test_missing_entity_helpers():
    available = {CanonicalEntity.SUBSCRIPTION}
    assert missing_tier_0_entities(available)
    assert CanonicalEntity.PRICE in missing_recommended_entities(available)
    assert tier_0_entities_complete(available)
    assert has_minimum_billing_entities(available)


def test_tier_0_complete_with_any_billing_file():
    from core.data_tiers import TIER_0_SOURCE_FILES

    assert tier_0_complete({FileType.SUBSCRIPTIONS})
    assert not tier_0_complete({FileType.CRM_CONTRACTS})
    assert FileType.PRICE_CATALOG in TIER_0_SOURCE_FILES
