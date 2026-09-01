import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from admin.service import (
    build_admin_overview,
    get_admin_assessment_detail,
    list_admin_accounts,
    list_admin_assessments,
    list_admin_audits,
    search_companies,
)
from models import Audit, Company, Report
from models.estimator import Assessment, AssessmentAnswer, LeadProfile


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


def test_get_admin_assessment_detail_serializes_answers():
    assessment = Assessment(session_token="token", status="completed", questionnaire_version="2.0")
    assessment.id = uuid.uuid4()
    assessment.lead_profile = LeadProfile(
        assessment_id=assessment.id,
        email="lead@example.com",
        company_name="Acme",
        role="CFO",
        lead_score=4,
        scan_intent=True,
    )
    assessment.answers = [
        AssessmentAnswer(
            assessment_id=assessment.id,
            question_id="profile.customer_count",
            section="profile",
            answer_type="number",
            value_numeric=120,
        )
    ]
    assessment.result = None

    db = MagicMock()
    assessment_query = MagicMock()
    assessment_query.options.return_value.filter.return_value.first.return_value = assessment

    audit_query = MagicMock()
    audit_query.filter.return_value.first.return_value = None

    model_run_query = MagicMock()
    model_run_query.filter.return_value.order_by.return_value.all.return_value = []

    db.query.side_effect = [assessment_query, audit_query, model_run_query]

    with patch("admin.service.get_question_by_id") as mock_question, patch(
        "admin.service.resolve_clerk_users", return_value={}
    ):
        mock_question.return_value = {"label": "About how many paying customers?"}
        detail = get_admin_assessment_detail(db, assessment.id)

    assert detail is not None
    assert detail["lead_email"] == "lead@example.com"
    assert detail["answers"][0]["display_value"] == "120"
    assert detail["answers"][0]["label"] == "About how many paying customers?"
