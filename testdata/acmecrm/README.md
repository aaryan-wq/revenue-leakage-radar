# AcmeCRM Test Dataset

Synthetic Stripe-like billing exports for **AcmeCRM**, a fictional B2B SaaS company. Use these files to upload through Revenue Leakage Radar or to run deterministic verification rule tests locally.

## Location

```
testdata/acmecrm/
├── customers.csv
├── subscriptions.csv
├── invoices.csv
├── invoice_line_items.csv
├── price_catalog.csv
├── coupons.csv
└── manifest.json
```

Regenerate at any time:

```bash
python scripts/generate_acmecrm_dataset.py
python scripts/verify_acmecrm_dataset.py
```

## Dataset Summary

| File | Rows | Description |
|------|------|-------------|
| customers.csv | 300 | Customer master |
| subscriptions.csv | 450 | ~60% monthly, ~40% annual |
| invoices.csv | ~4,470 | 24 months of billing history (Jun 2023 – Jun 2025) |
| invoice_line_items.csv | ~4,470 | One line item per invoice |
| price_catalog.csv | 24 | 6 tiers × 2 intervals × 2 catalog versions |
| coupons.csv | 4 | Active and expired promotional codes |

### Plans & Pricing

| Tier | Monthly | Annual | Product IDs |
|------|---------|--------|-------------|
| Starter | $49 | $490 | `prod_starter_mo` / `prod_starter_yr` |
| Growth | $99 | $990 | `prod_growth_mo` / `prod_growth_yr` |
| Professional | $199 | $1,990 | `prod_professional_mo` / `prod_professional_yr` |
| Business | $399 | $3,990 | `prod_business_mo` / `prod_business_yr` |
| Enterprise | $699 | $6,990 | `prod_enterprise_mo` / `prod_enterprise_yr` |
| Ultimate | $999 | $9,990 | `prod_ultimate_mo` / `prod_ultimate_yr` |

Catalog **v1** effective 2023-01-01. Catalog **v2** effective 2024-07-01 (+15% list price increase).

## Injected Revenue Leakage Scenarios

See `manifest.json` for exact subscription IDs. Each scenario maps to a verification rule:

| # | Scenario | Count | Rule ID | Subscription IDs |
|---|----------|-------|---------|------------------|
| 1 | Expired discounts still applied | 15 | `expired_discount_still_applied` | `sub_0001` – `sub_0015` |
| 2 | Legacy pricing after catalog v2 renewal | 10 | `legacy_sku_pricing_drift` | `sub_0016` – `sub_0025` |
| 3 | Invoice line item price ≠ subscription price | 8 | `invoice_subscription_price_mismatch` | See manifest |
| 4 | Duplicate discount stacking | 5 | `duplicate_discount_stacking` | `sub_0026` – `sub_0030` |
| 5 | Undercharged 10–20% vs catalog | 12 | `grandfathered_without_contract` | `sub_0031` – `sub_0042` |

### Scenario Details

1. **Expired discounts**, `LAUNCH20` (20% off, expired 2024-03-31) remains on subscription; post-expiry invoices still show invoice-level discount.
2. **Legacy pricing**, Subscriptions started on v1 catalog; renewed after 2024-07-01 but subscription price never migrated to v2.
3. **Line item mismatch**, Most recent invoice for 8 healthy subscriptions bills at 88% of subscription unit price.
4. **Duplicate discounts**, `PARTNER15` coupon on subscription plus an additional 10% invoice-level discount on every bill.
5. **Undercharged subscriptions**, Long-tenured active subscriptions priced 80–90% of current catalog with no CRM contract exception.

> **Note:** Expired-discount subscriptions (`sub_0001`–`sub_0015`) also satisfy duplicate-discount stacking. Overlapping findings are tagged **secondary** and excluded from headline totals.

## Expected Recoverable ARR (corrected engine)

After running attribution-aware verification on this dataset:

- **Primary recoverable ARR:** ~$3.19M (see `expected.json`)
- **Secondary excluded ARR:** ~$0.80M (overlapping findings kept for evidence)
- **Raw sum (all findings):** ~$4.0M

Regenerate bounds:

```bash
python scripts/generate_acmecrm_expected.py
python scripts/compare_acmecrm_leakage.py
```


## Upload

Upload all six CSV files for Tier 2+ coverage (full rule engine). Minimum Tier 0 (`invoice_line_items.csv` + `price_catalog.csv`) runs catalog mismatch rules only.
