# Verification Run, Seed 31760977

Fresh synthetic billing data with **one injected scenario per rule (25/25)**.

## Quick start

### 1. Upload test (24 rules via product UI)

Upload all 8 files from `upload/` (orphan line items excluded, upload validation blocks them):

- customers.csv, subscriptions.csv, invoices.csv, invoice_line_items.csv
- price_catalog.csv, coupons.csv, **accounts.csv**, **contracts.csv**

Start a **new audit** each time. Continue to validation → scan.

> Preview may show **22/25** rules before scan (credit/manual flags unknown pre-ingestion). After scan: **25/25** rules run; **24** produce upload findings. Rule `orphaned_records` is in `run_31760977/harness/` only.

### 2. Verify all 25 rules (engine)

```bash
python scripts/verify_verification_dataset.py --seed 31760977
```

Uses `harness/` CSVs (includes orphaned line item) to validate **25/25** injected scenarios.

### 3. Regenerate this exact dataset

```bash
python scripts/generate_verification_dataset.py --seed 31760977 --customers 100
```

## Injected leakage (ground truth)

| Metric | Value |
|--------|-------|
| Monthly (injected) | $9472.7100 |
| Annual (injected) | $107672.5200 |
| Upload scan primary ARR | $114502.52 |

Verification-mode datasets use a **clean baseline** plus one injection per rule. Headline recoverable ARR in the app should be **close to** injected annual leakage (typically within ~15%), not millions from baseline noise.

## Per-rule expected leakage

| Rule | Channel | Customer | Subscription | Monthly | Annual |
|------|---------|----------|--------------|---------|--------|
| `legacy_pricing` | upload | cust_00080 | sub_00080 | $700.4000 | $8404.8000 |
| `price_catalog_mismatch` | upload | cust_00078 | sub_00078 | $139.4000 | $1672.8000 |
| `grandfathered_pricing` | upload | cust_00012 | sub_00012 | $420.2400 | $5042.8800 |
| `missing_scheduled_increase` | upload | cust_00019 | sub_00019 | $191.3600 | $2296.3200 |
| `renewal_price_drift` | upload | cust_00090 | sub_00090 | $127.7100 | $1532.5200 |
| `manual_price_override` | upload | cust_00016 | sub_00016 | $1400.6400 | $16807.6800 |
| `incorrect_seat_price` | upload | cust_00033 | sub_00033 | $575.0000 | $6900.0000 |
| `incorrect_addon_price` | upload | cust_00045 | sub_00045 | $8.6200 | $103.4400 |
| `expired_discount` | upload | cust_00086 | sub_00086 | $255.5300 | $3066.3600 |
| `discount_stacking` | upload | cust_00049 | sub_00049 | $40.2500 | $483.0000 |
| `duplicate_discount` | upload | cust_00014 | sub_00014 | $46.4600 | $557.5200 |
| `permanent_promotional_discount` | upload | cust_00074 | sub_00074 | $0 | $0 |
| `excessive_discount` | upload | cust_00065 | sub_00065 | $10.0000 | $120.0000 |
| `discount_wrong_product` | upload | cust_00097 | sub_00097 | $28.7500 | $345.0000 |
| `invoice_price_mismatch` | upload | cust_00029 | sub_00029 | $82.8000 | $993.6000 |
| `duplicate_subscription` | upload | cust_00089 | sub_dup_cust_00089_1 | $57.5000 | $690.0000 |
| `billing_frequency_mismatch` | upload | cust_00094 | sub_00094 | $0 | $0 |
| `active_subscription_not_billing` | upload | cust_00039 | sub_free_cust_00039 | $57.50 | $690.00 |
| `cancelled_subscription_still_billing` | upload | cust_00026 | sub_00026 | $1045.3500 | $12544.2000 |
| `missing_expected_invoice` | upload | cust_00064 | sub_00064 | $3735.2000 | $44822.4000 |
| `credit_leakage` | upload | cust_00100 |, | $500.0000 | $0 |
| `duplicate_credit` | upload | cust_00071 |, | $50.0000 | $600.0000 |
| `duplicate_customer` | upload | cust_00051 |, | $0 | $0 |
| `currency_mismatch` | upload | cust_00011 | sub_00011 | $0 | $0 |
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
