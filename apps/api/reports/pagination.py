"""Paginated findings queries for report endpoints."""

from __future__ import annotations

from typing import Any, Literal

from sqlalchemy.orm import Session

from models import Finding, Report
from reports.entity_ids import EntityIdResolver
from reports.findings import build_primary_finding_lookup, serialize_finding
from verification.registry import RULES

FindingSort = Literal["arr_desc", "severity", "rule_id"]
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 25

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _category_rule_ids(category: str) -> list[str]:
    return [rule.rule_id for rule in RULES if rule.category == category]


def _apply_sort(query, sort: FindingSort):
    if sort == "rule_id":
        return query.order_by(Finding.rule_id.asc(), Finding.estimated_arr_loss.desc())
    if sort == "severity":
        return query.order_by(Finding.severity.asc(), Finding.estimated_arr_loss.desc())
    return query.order_by(Finding.estimated_arr_loss.desc(), Finding.id.asc())


def query_report_findings(
    db: Session,
    report: Report,
    *,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    sort: FindingSort = "arr_desc",
    category: str | None = None,
    evidence_record_limit: int | None = 3,
) -> dict[str, Any]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)

    base_query = db.query(Finding).filter(Finding.audit_id == report.audit_id)
    if category:
        rule_ids = _category_rule_ids(category)
        if not rule_ids:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "has_more": False,
            }
        base_query = base_query.filter(Finding.rule_id.in_(rule_ids))

    total = base_query.count()
    offset = (page - 1) * page_size
    findings = _apply_sort(base_query, sort).offset(offset).limit(page_size).all()

    entity_resolver = EntityIdResolver.for_findings(db, findings)
    primary_refs = {finding.primary_finding_ref for finding in findings if finding.primary_finding_ref}
    referenced_primaries: list[Finding] = []
    if primary_refs:
        referenced_primaries = (
            db.query(Finding)
            .filter(
                Finding.audit_id == report.audit_id,
                Finding.finding_ref.in_(primary_refs),
            )
            .all()
        )
    primary_by_ref = build_primary_finding_lookup(referenced_primaries)

    items = [
        serialize_finding(
            finding,
            include_evidence=True,
            evidence_record_limit=evidence_record_limit,
            entity_resolver=entity_resolver,
            primary_by_ref=primary_by_ref,
        )
        for finding in findings
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": offset + len(items) < total,
    }


def build_primary_lookup_for_finding(db: Session, finding: Finding) -> dict[str, Finding]:
    if not finding.primary_finding_ref:
        return {}

    primary = (
        db.query(Finding)
        .filter(
            Finding.audit_id == finding.audit_id,
            Finding.finding_ref == finding.primary_finding_ref,
        )
        .first()
    )
    if not primary:
        return {}

    return build_primary_finding_lookup([primary])
