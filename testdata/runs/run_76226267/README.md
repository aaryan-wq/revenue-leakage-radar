# Verification Run, Seed 76226267

Fresh synthetic billing data with **one injected scenario per rule (25/25)**.

## Quick start

### 1. Upload test (24 rules via product UI)

Upload all 8 files from `upload/`:

- customers.csv, subscriptions.csv, invoices.csv, invoice_line_items.csv
- price_catalog.csv, coupons.csv, **accounts.csv**, **contracts.csv**

Start a **new audit** each time. Continue to validation → scan.

> Preview may show **22/25** rules before scan (credit/manual flags unknown pre-ingestion). After scan: **25/25** run; **24** produce findings (`orphaned_records` needs harness).

### 2. Verify all 25 rules (engine)

```bash
python scripts/verify_verification_dataset.py --seed 76226267
```

### 3. Regenerate this exact dataset

```bash
python scripts/generate_verification_dataset.py --seed 76226267 --customers 100
```

## Injected leakage (ground truth)

| Metric | Value |
|--------|-------|
| Monthly (injected) | $9665.1700 |
| Annual (injected) | $109982.0400 |
| Upload scan primary ARR | $105358.40 |

Verification-mode datasets use a **clean baseline** plus one injection per rule. Headline recoverable ARR in the app should be **close to** injected annual leakage (typically within ~15%), not millions from baseline noise.

## Per-rule expected leakage

| Rule | Channel | Customer | Subscription | Monthly | Annual |
|------|---------|----------|--------------|---------|--------|
| `legacy_pricing` | upload | cust_00025 | sub_00025 | $109.6800 | $1316.1600 |
| `price_catalog_mismatch` | upload | cust_00029 | sub_00029 | $36.5500 | $438.6000 |
| `grandfathered_pricing` | upload | cust_00015 | sub_00015 | $219.4200 | $2633.0400 |
| `missing_scheduled_increase` | upload | cust_00032 | sub_00032 | $516.1200 | $6193.4400 |
| `renewal_price_drift` | upload | cust_00016 | sub_00016 | $516.1200 | $6193.4400 |
| `manual_price_override` | upload | cust_00083 | sub_00083 | $609.5000 | $7314.0000 |
| `incorrect_seat_price` | upload | cust_00055 | sub_00055 | $2438.0000 | $29256.0000 |
| `incorrect_addon_price` | upload | cust_00057 | sub_00057 | $9.1400 | $109.6800 |
| `expired_discount` | upload | cust_00017 | sub_00017 | $36.5700 | $438.8400 |
| `discount_stacking` | upload | cust_00095 | sub_00095 | $170.6600 | $2047.9200 |
| `duplicate_discount` | upload | cust_00070 | sub_00070 | $104.8800 | $1258.5600 |
| `permanent_promotional_discount` | upload | cust_00044 | sub_00044 | $0 | $0 |
| `excessive_discount` | upload | cust_00002 | sub_00002 | $10.0000 | $120.0000 |
| `discount_wrong_product` | upload | cust_00049 | sub_00049 | $30.4700 | $365.6400 |
| `invoice_price_mismatch` | upload | cust_00082 | sub_00082 | $188.7600 | $2265.1200 |
| `duplicate_subscription` | upload | cust_00092 | sub_dup_cust_00092_1 | $60.9500 | $731.4000 |
| `billing_frequency_mismatch` | upload | cust_00098 | sub_00098 | $0 | $0 |
| `active_subscription_not_billing` | upload | cust_00089 | sub_free_cust_00089 | $60.95 | $731.40 |
| `cancelled_subscription_still_billing` | upload | cust_00093 | sub_00093 | $243.8000 | $2925.6000 |
| `missing_expected_invoice` | upload | cust_00076 | sub_00076 | $3753.6000 | $45043.2000 |
| `credit_leakage` | upload | cust_00058 |, | $500.0000 | $0 |
| `duplicate_credit` | upload | cust_00068 |, | $50.0000 | $600.0000 |
| `duplicate_customer` | upload | cust_00006 |, | $0 | $0 |
| `currency_mismatch` | upload | cust_00088 | sub_00088 | $0 | $0 |
| `orphaned_records` | harness only | cust_00001 |, | $0 | $0 |

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

## orphaned_records (rule 25)

Upload validation blocks line items with missing invoice parents. Rule 25 is verified via harness using seed `76226267`, not via CSV upload.
