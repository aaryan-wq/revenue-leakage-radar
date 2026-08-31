import uuid
from unittest.mock import MagicMock, patch

import pytest

from admin.service import admin_refund_purchase, create_support_note, list_support_notes
from models import ReportPurchase, SupportNote


def test_create_support_note_persists():
    db = MagicMock()
    note = SupportNote(
        entity_type="audit",
        entity_id="abc",
        author_clerk_user_id="admin_1",
        body="Follow up with customer",
    )
    note.id = uuid.uuid4()

    def refresh_side_effect(obj):
        obj.id = note.id

    db.refresh.side_effect = refresh_side_effect

    with patch("admin.service.SupportNote", return_value=note):
        created = create_support_note(
            db,
            entity_type="audit",
            entity_id="abc",
            author_clerk_user_id="admin_1",
            body="Follow up with customer",
        )

    db.add.assert_called_once()
    db.commit.assert_called_once()
    assert created.body == "Follow up with customer"


def test_list_support_notes_filters_by_entity():
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value = query
    query.count.return_value = 0
    query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

    result = list_support_notes(
        db,
        entity_type="report",
        entity_id="report-1",
        page=1,
        page_size=25,
    )

    assert result["total"] == 0
    assert result["items"] == []


def test_admin_refund_purchase_updates_status():
    purchase = ReportPurchase(
        clerk_user_id="user_1",
        plan="single_report",
        stripe_payment_intent_id="pi_123",
        status="completed",
    )
    purchase.id = uuid.uuid4()
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = purchase

    with patch("admin.service.ensure_stripe_configured"):
        with patch("admin.service.stripe.Refund.create") as mock_refund:
            with patch("admin.service.get_report_by_id", return_value=None):
                with patch("admin.service.create_support_note"):
                    result = admin_refund_purchase(
                        db,
                        purchase_id=purchase.id,
                        reason="duplicate charge",
                        admin_user_id="admin_1",
                    )

    mock_refund.assert_called_once()
    assert purchase.status == "refunded"
    assert result["status"] == "refunded"
