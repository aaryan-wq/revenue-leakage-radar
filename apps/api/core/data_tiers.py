"""Data tier framework for adaptive ingestion and entity-based rule gating."""

from core.canonical_entities import (
    CanonicalEntity,
    MINIMUM_BILLING_ENTITIES,
    TIER_0_REQUIRED_ENTITIES,
    TIER_0_SOURCE_FILES,
    TIER_1_RECOMMENDED_ENTITIES,
    TIER_1_RECOMMENDED_SOURCE_FILES,
    TIER_2_OPTIONAL_ENTITIES,
    TIER_2_OPTIONAL_SOURCE_FILES,
    TIER_3_OPTIONAL_ENTITIES,
    TIER_3_OPTIONAL_SOURCE_FILES,
    entities_from_uploaded_files,
)
from core.enums import DataTier, FileType

# Backward-compatible aliases for upload validation (source file proxies)
TIER_0_REQUIRED: frozenset[FileType] = TIER_0_SOURCE_FILES
TIER_1_RECOMMENDED: frozenset[FileType] = TIER_1_RECOMMENDED_SOURCE_FILES
TIER_2_OPTIONAL: frozenset[FileType] = TIER_2_OPTIONAL_SOURCE_FILES
TIER_3_OPTIONAL: frozenset[FileType] = TIER_3_OPTIONAL_SOURCE_FILES

FILE_TYPE_TIER: dict[FileType, DataTier] = {
    **{ft: DataTier.TIER_0 for ft in TIER_0_SOURCE_FILES},
    **{ft: DataTier.TIER_1 for ft in TIER_1_RECOMMENDED_SOURCE_FILES},
    **{ft: DataTier.TIER_2_PLUS for ft in TIER_2_OPTIONAL_SOURCE_FILES},
    **{ft: DataTier.TIER_2_PLUS for ft in TIER_3_OPTIONAL_SOURCE_FILES},
}

ALL_BILLING_FILE_TYPES: frozenset[FileType] = (
    TIER_0_SOURCE_FILES | TIER_1_RECOMMENDED_SOURCE_FILES | TIER_2_OPTIONAL_SOURCE_FILES
)


def missing_tier_0_files(uploaded: set[FileType]) -> list[FileType]:
    return sorted(TIER_0_SOURCE_FILES - uploaded, key=lambda ft: ft.value)


def missing_recommended_files(uploaded: set[FileType]) -> list[FileType]:
    return sorted(TIER_1_RECOMMENDED_SOURCE_FILES - uploaded, key=lambda ft: ft.value)


def tier_0_complete(uploaded: set[FileType]) -> bool:
    return bool(uploaded & TIER_0_SOURCE_FILES)


def has_minimum_billing_entities(available: set[CanonicalEntity]) -> bool:
    return bool(available & MINIMUM_BILLING_ENTITIES)


def tier_0_entities_complete(available: set[CanonicalEntity]) -> bool:
    return has_minimum_billing_entities(available)


def missing_entities(available: set[CanonicalEntity], required: frozenset[CanonicalEntity]) -> set[CanonicalEntity]:
    return required - available


def entity_available(available: set[CanonicalEntity], required: frozenset[CanonicalEntity]) -> bool:
    return required.issubset(available)


def missing_tier_0_entities(available: set[CanonicalEntity]) -> list[CanonicalEntity]:
    return sorted(MINIMUM_BILLING_ENTITIES - available, key=lambda entity: entity.value)


def missing_recommended_entities(available: set[CanonicalEntity]) -> list[CanonicalEntity]:
    return sorted(TIER_1_RECOMMENDED_ENTITIES - available, key=lambda entity: entity.value)


def get_audit_data_tier(available: set[CanonicalEntity] | set[FileType]) -> DataTier:
    if available and isinstance(next(iter(available)), FileType):
        return get_audit_data_tier_from_uploads(set(available))  # type: ignore[arg-type]
    entities = set(available)  # type: ignore[arg-type]
    if not has_minimum_billing_entities(entities):
        return DataTier.INSUFFICIENT
    if TIER_1_RECOMMENDED_ENTITIES.issubset(entities):
        if TIER_2_OPTIONAL_ENTITIES.issubset(entities) or any(
            entity in entities for entity in TIER_3_OPTIONAL_ENTITIES
        ):
            return DataTier.TIER_2_PLUS
        return DataTier.TIER_1
    return DataTier.TIER_0


def get_audit_data_tier_from_uploads(uploaded: set[FileType]) -> DataTier:
    return get_audit_data_tier(entities_from_uploaded_files(uploaded))


def get_audit_data_tier_from_entities(available: set[CanonicalEntity]) -> DataTier:
    return get_audit_data_tier(available)


# Deprecated, use missing_entities / entity_available
def dataset_available(uploaded: set[FileType], required: frozenset[FileType]) -> bool:
    return required.issubset(uploaded)


def missing_datasets(uploaded: set[FileType], required: frozenset[FileType]) -> set[FileType]:
    return required - uploaded
