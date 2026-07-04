"""Unit tests for catalog lookup priority in AuditContext."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from models import PriceCatalog
from verification.context import AuditContext


def test_catalog_for_product_prefers_product_id_over_shared_sku():
    company_id = uuid.uuid4()
    ctx = AuditContext(
        audit_id=uuid.uuid4(),
        company_id=company_id,
        price_catalog=[
            PriceCatalog(
                id=uuid.uuid4(),
                company_id=company_id,
                product_id="prod_starter_mo",
                sku="SKU-STAR-MO",
                list_price=Decimal("57.50"),
                effective_date=datetime(2024, 7, 1, tzinfo=timezone.utc),
                billing_interval="monthly",
            ),
            PriceCatalog(
                id=uuid.uuid4(),
                company_id=company_id,
                product_id="prod_starter_yr",
                sku="SKU-STAR-YR",
                list_price=Decimal("575.00"),
                effective_date=datetime(2024, 7, 1, tzinfo=timezone.utc),
                billing_interval="annual",
            ),
        ],
    )

    annual = ctx.catalog_for_product("prod_starter_yr", "SKU-STAR-MO")
    assert annual is not None
    assert annual.product_id == "prod_starter_yr"
    assert annual.list_price == Decimal("575.00")
