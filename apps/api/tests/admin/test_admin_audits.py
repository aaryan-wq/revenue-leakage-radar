import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from admin.service import build_admin_overview, list_admin_audits, search_companies
from models import Audit, Company, Report


def test_build_admin_overview_returns_shape():
    db = MagicMock()
    db.query.return_value.scalar.side_effect = [5, 4, 10, Decimal("120000"), 1, 1]
    db.query.return_value.filter.return_value.scalar.side_effect = [3, 2, 1, 1]

    overview = build_admin_overview(db)

    assert overview["total_audits"] == 5
    assert overview["linked_users"] == 3
    assert overview["total_reports"] == 4
    assert overview["purchased_reports"] == 2
    assert overview["total_recoverable_arr"] == "120000"


def test_search_companies_returns_items():
    company = Company(name="Acme Corp")
    company.id = uuid.uuid4()
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value = query
    query.count.return_value = 1
    query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [company]
    db.query.return_value.filter.return_value.scalar.return_value = 2

    result = search_companies(db, q="acme", page=1, page_size=25)

    assert result["total"] == 1
    assert result["items"][0]["name"] == "Acme Corp"
    assert result["items"][0]["audit_count"] == 2


def test_list_admin_audits_serializes_report_fields():
    company = Company(name="Northwind")
    company.id = uuid.uuid4()
    audit = Audit(session_token="token", status="completed", clerk_user_id="user_1")
    audit.id = uuid.uuid4()
    audit.company = company
    report = Report(
        audit_id=audit.id,
        recoverable_arr=Decimal("5000"),
        finding_count=3,
        purchased=True,
    )
    report.id = uuid.uuid4()
    audit.report = report

    db = MagicMock()
    query = db.query.return_value.options.return_value
    query.filter.return_value = query
    query.count.return_value = 1
    query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [audit]

    result = list_admin_audits(db, q=None, page=1, page_size=25)

    item = result["items"][0]
    assert item["company_name"] == "Northwind"
    assert item["recoverable_arr"] == "5000"
    assert item["purchased"] is True
