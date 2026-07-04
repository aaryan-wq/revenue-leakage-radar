# Verification Run, Seed 991337

Fresh synthetic billing data with **one injected scenario per rule (25/25)**.

## Quick start

### 1. Upload test (24 rules via product UI)

Upload all 8 files from `upload/` (orphan line items excluded, upload validation blocks them):

- customers.csv, subscriptions.csv, invoices.csv, invoice_line_items.csv
- price_catalog.csv, coupons.csv, **accounts.csv**, **contracts.csv**

Start a **new audit** each time. Continue to validation → scan.

> Preview may show **22/25** rules before scan (credit/manual flags unknown pre-ingestion). After scan: **25/25** rules run; **24** produce upload findings. Rule `orphaned_records` is in `run_991337/harness/` only.

### 2. Verify all 25 rules (engine)

```bash
python scripts/verify_verification_dataset.py --seed 991337
```

Uses `harness/` CSVs (includes orphaned line item) to validate **25/25** injected scenarios.

### 3. Regenerate this exact dataset

```bash
python scripts/generate_verification_dataset.py --seed 991337 --customers 100
```

## Injected leakage (ground truth)

| Metric | Value |
|--------|-------|
| Monthly (injected) | $11668.6300 |
| Annual (injected) | $134023.5600 |
| Upload scan primary ARR | $142907.96 |

Verification-mode datasets use a **clean baseline** plus one injection per rule. Headline recoverable ARR in the app should be **close to** injected annual leakage (typically within ~15%), not millions from baseline noise.

## Per-rule expected leakage

| Rule | Channel | Customer | Subscription | Monthly | Annual |
|------|---------|----------|--------------|---------|--------|
| `legacy_pricing` | upload | cust_00078 | sub_00078 | $154.5600 | $1854.7200 |
| `price_catalog_mismatch` | upload | cust_00071 | sub_00071 | $112.0400 | $1344.4800 |
| `grandfathered_pricing` | upload | cust_00032 | sub_00032 | $554.7200 | $6656.6400 |
| `missing_scheduled_increase` | upload | cust_00048 | sub_00048 | $554.7600 | $6657.1200 |
| `renewal_price_drift` | upload | cust_00098 | sub_00098 | $77.2800 | $927.3600 |
| `manual_price_override` | upload | cust_00017 | sub_00017 | $110.4000 | $1324.8000 |
| `incorrect_seat_price` | upload | cust_00080 | sub_00080 | $4623.0000 | $55476.0000 |
| `incorrect_addon_price` | upload | cust_00077 | sub_00077 | $11.0400 | $132.4800 |
| `expired_discount` | upload | cust_00004 | sub_00004 | $647.2200 | $7766.6400 |
| `discount_stacking` | upload | cust_00019 | sub_00019 | $163.4200 | $1961.0400 |
| `duplicate_discount` | upload | cust_00046 | sub_00046 | $103.0400 | $1236.4800 |
| `permanent_promotional_discount` | upload | cust_00027 | sub_00027 | $0 | $0 |
| `excessive_discount` | upload | cust_00087 | sub_00087 | $10.0000 | $120.0000 |
| `discount_wrong_product` | upload | cust_00076 | sub_00076 | $231.1500 | $2773.8000 |
| `invoice_price_mismatch` | upload | cust_00075 | sub_00075 | $140.0500 | $1680.6000 |
| `duplicate_subscription` | upload | cust_00003 | sub_dup_cust_00003_1 | $73.6000 | $883.2000 |
| `billing_frequency_mismatch` | upload | cust_00041 | sub_00041 | $0 | $0 |
| `active_subscription_not_billing` | upload | cust_00038 | sub_free_cust_00038 | $73.60 | $883.20 |
| `cancelled_subscription_still_billing` | upload | cust_00055 | sub_00055 | $1167.2500 | $14007.0000 |
| `missing_expected_invoice` | upload | cust_00088 | sub_00088 | $2311.5000 | $27738.0000 |
| `credit_leakage` | upload | cust_00009 |, | $500.0000 | $0 |
| `duplicate_credit` | upload | cust_00059 |, | $50.0000 | $600.0000 |
| `duplicate_customer` | upload | cust_00079 |, | $0 | $0 |
| `currency_mismatch` | upload | cust_00006 | sub_00006 | $0 | $0 |
| `orphaned_records` | harness | cust_00001 |, | $0 | $0 |

## Files

| File | Rows |
|------|------|
| customers.csv | 100 |
| subscriptions.csv | 103 |
| invoices.csv | 2312 |
| invoice_line_items.csv | 2307 |
| price_catalog.csv | 10 |
| coupons.csv | 3 |
| accounts.csv | 100 |
| contracts.csv | 2 |

## harness/ (all 25 rules)

Same 8 files as upload, but `invoice_line_items.csv` **includes** the orphaned line item for rule `orphaned_records`. Use for engine verification, not for product upload.
