# Verification Run, Seed 76155281

Fresh synthetic billing data with **one injected scenario per rule (25/25)**.

## Quick start

### 1. Upload test (24 rules via product UI)

Upload all 8 files from `upload/` (orphan line items excluded, upload validation blocks them):

- customers.csv, subscriptions.csv, invoices.csv, invoice_line_items.csv
- price_catalog.csv, coupons.csv, **accounts.csv**, **contracts.csv**

Start a **new audit** each time. Continue to validation → scan.

> Preview may show **22/25** rules before scan (credit/manual flags unknown pre-ingestion). After scan: **25/25** rules run; **24** produce upload findings. Rule `orphaned_records` is in `run_76155281/harness/` only.

### 2. Verify all 25 rules (engine)

```bash
python scripts/verify_verification_dataset.py --seed 76155281
```

Uses `harness/` CSVs (includes orphaned line item) to validate **25/25** injected scenarios.

### 3. Regenerate this exact dataset

```bash
python scripts/generate_verification_dataset.py --seed 76155281 --customers 100
```

## Injected leakage (ground truth)

| Metric | Value |
|--------|-------|
| Monthly (injected) | $10343.3900 |
| Annual (injected) | $118120.6800 |
| Upload scan primary ARR | $135847.40 |

Verification-mode datasets use a **clean baseline** plus one injection per rule. Headline recoverable ARR in the app should be **close to** injected annual leakage (typically within ~15%), not millions from baseline noise.

## Per-rule expected leakage

| Rule | Channel | Customer | Subscription | Monthly | Annual |
|------|---------|----------|--------------|---------|--------|
| `legacy_pricing` | upload | cust_00063 | sub_00063 | $324.4500 | $3893.4000 |
| `price_catalog_mismatch` | upload | cust_00011 | sub_00011 | $259.5600 | $3114.7200 |
| `grandfathered_pricing` | upload | cust_00044 | sub_00044 | $282.8800 | $3394.5600 |
| `missing_scheduled_increase` | upload | cust_00060 | sub_00060 | $235.7500 | $2829.0000 |
| `renewal_price_drift` | upload | cust_00013 | sub_00013 | $89.6400 | $1075.6800 |
| `manual_price_override` | upload | cust_00019 | sub_00019 | $600.9000 | $7210.8000 |
| `incorrect_seat_price` | upload | cust_00056 | sub_00056 | $4715.0000 | $56580.0000 |
| `incorrect_addon_price` | upload | cust_00077 | sub_00077 | $11.2100 | $134.5200 |
| `expired_discount` | upload | cust_00094 | sub_00094 | $124.2000 | $1490.4000 |
| `discount_stacking` | upload | cust_00012 | sub_00012 | $424.3500 | $5092.2000 |
| `duplicate_discount` | upload | cust_00035 | sub_00035 | $192.2800 | $2307.3600 |
| `permanent_promotional_discount` | upload | cust_00027 | sub_00027 | $0 | $0 |
| `excessive_discount` | upload | cust_00090 | sub_00090 | $10.0000 | $120.0000 |
| `discount_wrong_product` | upload | cust_00089 | sub_00089 | $37.3700 | $448.4400 |
| `invoice_price_mismatch` | upload | cust_00074 | sub_00074 | $149.0000 | $1788.0000 |
| `duplicate_subscription` | upload | cust_00023 | sub_dup_cust_00023_1 | $74.7500 | $897.0000 |
| `billing_frequency_mismatch` | upload | cust_00066 | sub_00066 | $0 | $0 |
| `active_subscription_not_billing` | upload | cust_00017 | sub_free_cust_00017 | $74.75 | $897.00 |
| `cancelled_subscription_still_billing` | upload | cust_00087 | sub_00087 | $1442.1000 | $17305.2000 |
| `missing_expected_invoice` | upload | cust_00034 | sub_00034 | $745.2000 | $8942.4000 |
| `credit_leakage` | upload | cust_00006 |, | $500.0000 | $0 |
| `duplicate_credit` | upload | cust_00036 |, | $50.0000 | $600.0000 |
| `duplicate_customer` | upload | cust_00010 |, | $0 | $0 |
| `currency_mismatch` | upload | cust_00052 | sub_00052 | $0 | $0 |
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
