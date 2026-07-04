import csv
import io

from models import Finding, Report
from reports.findings import build_primary_finding_lookup, parse_evidence, serialize_finding
from reports.entity_ids import EntityIdResolver
from sqlalchemy.orm import Session

FINDINGS_CSV_HEADERS = [
    "id",
    "rule_id",
    "title",
    "category",
    "severity",
    "confidence",
    "estimated_monthly_loss",
    "estimated_arr_loss",
    "customer_id",
    "subscription_id",
    "invoice_id",
    "recommendation",
]


def build_findings_csv(db: Session, report: Report) -> bytes:
    findings = (
        db.query(Finding)
        .filter(Finding.audit_id == report.audit_id)
        .order_by(Finding.estimated_arr_loss.desc())
        .all()
    )
    entity_resolver = EntityIdResolver.for_findings(db, findings)
    primary_by_ref = build_primary_finding_lookup(findings)

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=FINDINGS_CSV_HEADERS)
    writer.writeheader()
    for finding in findings:
        payload = serialize_finding(
            finding,
            entity_resolver=entity_resolver,
            primary_by_ref=primary_by_ref,
        )
        writer.writerow({key: payload.get(key, "") for key in FINDINGS_CSV_HEADERS})
    return buffer.getvalue().encode("utf-8")


def build_evidence_csv(db: Session, report: Report) -> bytes:
    findings = db.query(Finding).filter(Finding.audit_id == report.audit_id).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "finding_id",
            "rule_id",
            "field",
            "expected",
            "actual",
            "reference_ids",
        ]
    )
    for finding in findings:
        evidence = parse_evidence(finding.evidence)
        for record in evidence.get("records", []):
            writer.writerow(
                [
                    str(finding.id),
                    finding.rule_id,
                    record.get("field", ""),
                    record.get("expected", ""),
                    record.get("actual", ""),
                    str(record.get("reference_ids", {})),
                ]
            )
    return buffer.getvalue().encode("utf-8")
