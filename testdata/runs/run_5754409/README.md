# Verification Run, Seed 5754409

Fresh synthetic billing data with **one injected scenario per rule (25/25)**.

## Quick start

### 1. Upload test (24 rules via product UI)

Upload all 8 files from `upload/` (orphan line items excluded, upload validation blocks them):

- customers.csv, subscriptions.csv, invoices.csv, invoice_line_items.csv
- price_catalog.csv, coupons.csv, **accounts.csv**, **contracts.csv**

Start a **new audit** each time. Continue to validation → scan.

> Preview may show **22/25** rules before scan (credit/manual flags unknown pre-ingestion). After scan: **25/25** rules run; **24** produce upload findings. Rule `orphaned_records` is in `run_5754409/harness/` only.

### 2. Verify all 25 rules (engine)

```bash
python scripts/verify_verification_dataset.py --seed 5754409
```

Uses `harness/` CSVs (includes orphaned line item) to validate **25/25** injected scenarios.

### 3. Regenerate this exact dataset

```bash
python scripts/generate_verification_dataset.py --seed 5754409 --customers 100
```

## Injected leakage (ground truth)

| Metric | Value |
|--------|-------|
| Monthly (injected) | $9452.1500 |
| Annual (injected) | $107425.8000 |
| Upload scan primary ARR | $111219.20 |

Verification-mode datasets use a **clean baseline** plus one injection per rule. Headline recoverable ARR in the app should be **close to** injected annual leakage (typically within ~15%), not millions from baseline noise.

## Per-rule expected leakage

| Rule | Channel | Customer | Subscription | Monthly | Annual |
|------|---------|----------|--------------|---------|--------|
| `legacy_pricing` | upload | cust_00002 | sub_00002 | $196.6000 | $2359.2000 |
| `price_catalog_mismatch` | upload | cust_00057 | sub_00057 | $92.7600 | $1113.1200 |
| `grandfathered_pricing` | upload | cust_00096 | sub_00096 | $498.6800 | $5984.1600 |
| `missing_scheduled_increase` | upload | cust_00091 | sub_00091 | $243.8000 | $2925.6000 |
| `renewal_price_drift` | upload | cust_00007 | sub_00007 | $121.9000 | $1462.8000 |
| `manual_price_override` | upload | cust_00022 | sub_00022 | $196.6800 | $2360.1600 |
| `incorrect_seat_price` | upload | cust_00086 | sub_00086 | $1311.0000 | $15732.0000 |
| `incorrect_addon_price` | upload | cust_00048 | sub_00048 | $71.2400 | $854.8800 |
| `expired_discount` | upload | cust_00023 | sub_00023 | $195.0400 | $2340.4800 |
| `discount_stacking` | upload | cust_00094 | sub_00094 | $131.1000 | $1573.2000 |
| `duplicate_discount` | upload | cust_00092 | sub_00092 | $332.4700 | $3989.6400 |
| `permanent_promotional_discount` | upload | cust_00081 | sub_00081 | $0 | $0 |
| `excessive_discount` | upload | cust_00054 | sub_00054 | $10.0000 | $120.0000 |
| `discount_wrong_product` | upload | cust_00068 | sub_00068 | $237.4700 | $2849.6400 |
| `invoice_price_mismatch` | upload | cust_00083 | sub_00083 | $321.8600 | $3862.3200 |
| `duplicate_subscription` | upload | cust_00034 | sub_dup_cust_00034_1 | $64.4000 | $772.8000 |
| `billing_frequency_mismatch` | upload | cust_00059 | sub_00059 | $0 | $0 |
| `active_subscription_not_billing` | upload | cust_00020 | sub_free_cust_00020 | $64.40 | $772.80 |
| `cancelled_subscription_still_billing` | upload | cust_00095 | sub_00095 | $2438.0000 | $29256.0000 |
| `missing_expected_invoice` | upload | cust_00012 | sub_00012 | $2374.7500 | $28497.0000 |
| `credit_leakage` | upload | cust_00088 |, | $500.0000 | $0 |
| `duplicate_credit` | upload | cust_00032 |, | $50.0000 | $600.0000 |
| `duplicate_customer` | upload | cust_00018 |, | $0 | $0 |
| `currency_mismatch` | upload | cust_00079 | sub_00079 | $0 | $0 |
| `orphaned_records` | harness | cust_00001 |, | $0 | $0 |

## Files

| File | Rows |
|------|------|
| customers.csv | 100 |
| subscriptions.csv | 103 |
| invoices.csv | 2312 |
| invoice_line_items.csv | 2307 |
| price_catalog.csv | 9 |
| coupons.csv | 3 |
| accounts.csv | 100 |
| contracts.csv | 2 |

## harness/ (all 25 rules)

Same 8 files as upload, but `invoice_line_items.csv` **includes** the orphaned line item for rule `orphaned_records`. Use for engine verification, not for product upload.
