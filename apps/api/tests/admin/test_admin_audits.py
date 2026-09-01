import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from admin.service import build_admin_overview, list_admin_audits, list_admin_assessments, list_admin_accounts, search_companies
from models import Audit, Company, Report


def test_build_admin_overview_returns_shape():
    db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.scalar.side_effect = [
        5, 3, 1, 4, 4, 2, 10, 1,
        Decimal("120000"), Decimal("30000"), 250000,
        1, 2, 1, 2, 6, 2,
        8, 5, 2, 4, 3, 1, 2,
    ]
    db.query.return_value = mock_query

    overview = build_admin_overview(db)

    assert overview["total_audits"] == 5
    assert overview["linked_users"] == 3
    assert overview["total_reports"] == 4
    assert overview["total_recoverable_arr"] == "120000"
    assert overview["total_assessments"] == 8
    assert overview["assessments_with_leads"] == 3


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


def test_list_admin_audits_serializes_report_and_user_fields():
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

    with patch("admin.service.resolve_clerk_users") as mock_users:
        mock_users.return_value = {
            "user_1": MagicMock(display_name="Aaryan Singh", email="aaryan@paevo.co"),
        }
        result = list_admin_audits(db, q=None, page=1, page_size=25)

    item = result["items"][0]
    assert item["company_name"] == "Northwind"
    assert item["recoverable_arr"] == "5000"
    assert item["purchased"] is True
    assert item["clerk_user_name"] == "Aaryan Singh"
    assert item["clerk_user_email"] == "aaryan@paevo.co"


def test_list_admin_assessments_returns_items():
    db = MagicMock()
    query = db.query.return_value.options.return_value
    query.filter.return_value = query
    query.outerjoin.return_value.filter.return_value = query
    query.count.return_value = 0
    query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

    result = list_admin_assessments(db, q=None, status=None, page=1, page_size=25)
    assert result["items"] == []
    assert result["total"] == 0


def test_list_admin_accounts_returns_items():
    db = MagicMock()
    base = db.query.return_value.outerjoin.return_value.outerjoin.return_value.outerjoin.return_value
    base.count.return_value = 0
    base.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

    with patch("admin.service.resolve_clerk_users", return_value={}):
        result = list_admin_accounts(db, q=None, page=1, page_size=25)

    assert result["items"] == []
    assert result["total"] == 0
