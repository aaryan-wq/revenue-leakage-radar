"""Normalize adapter output into canonical database entities."""

from sqlalchemy.orm import Session

from canonical.transformer import run_canonical_transform
from core.canonical_entities import entities_from_counts
from ingestion.types import IngestionContext
from models import Audit


def normalize_to_canonical(db: Session, audit: Audit, ctx: IngestionContext):
    result = run_canonical_transform(db, audit, ctx)
    available = entities_from_counts(result.counts)
    ctx.available_entities = available
    audit.available_entities = sorted(entity.value for entity in available)
    return result
