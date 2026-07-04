# Verification Run, Seed 3437452345

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
python scripts/verify_verification_dataset.py --seed 3437452345
```

### 3. Regenerate this exact dataset

```bash
python scripts/generate_verification_dataset.py --seed 3437452345 --customers 100
```

## Injected leakage (ground truth)

| Metric | Value |
|--------|-------|
| Monthly (injected) | $12313.2400 |
| Annual (injected) | $141758.8800 |
| Upload scan primary ARR | $168874.16 |

Verification-mode datasets use a **clean baseline** plus one injection per rule. Headline recoverable ARR in the app should be **close to** injected annual leakage (typically within ~15%), not millions from baseline noise.

## Per-rule expected leakage

| Rule | Channel | Customer | Subscription | Monthly | Annual |
|------|---------|----------|--------------|---------|--------|
| `legacy_pricing` | upload | cust_00036 | sub_00036 | $207.0000 | $2484.0000 |
| `price_catalog_mismatch` | upload | cust_00054 | sub_00054 | $182.1600 | $2185.9200 |
| `grandfathered_pricing` | upload | cust_00025 | sub_00025 | $30.0000 | $360.0000 |
| `missing_scheduled_increase` | upload | cust_00075 | sub_00075 | $298.0800 | $3576.9600 |
| `renewal_price_drift` | upload | cust_00080 | sub_00080 | $138.0000 | $1656.0000 |
| `manual_price_override` | upload | cust_00081 | sub_00081 | $183.4800 | $2201.7600 |
| `incorrect_seat_price` | upload | cust_00092 | sub_00092 | $4600.0000 | $55200.0000 |
| `incorrect_addon_price` | upload | cust_00011 | sub_00011 | $37.2600 | $447.1200 |
| `expired_discount` | upload | cust_00040 | sub_00040 | $276.0000 | $3312.0000 |
| `discount_stacking` | upload | cust_00089 | sub_00089 | $60.0300 | $720.3600 |
| `duplicate_discount` | upload | cust_00014 | sub_00014 | $139.1500 | $1669.8000 |
| `permanent_promotional_discount` | upload | cust_00074 | sub_00074 | $0 | $0 |
| `excessive_discount` | upload | cust_00041 | sub_00041 | $10.0000 | $120.0000 |
| `discount_wrong_product` | upload | cust_00067 | sub_00067 | $124.2000 | $1490.4000 |
| `invoice_price_mismatch` | upload | cust_00099 | sub_00099 | $238.4800 | $2861.7600 |
| `duplicate_subscription` | upload | cust_00013 | sub_dup_cust_00013_1 | $66.7000 | $800.4000 |
| `billing_frequency_mismatch` | upload | cust_00043 | sub_00043 | $0 | $0 |
| `active_subscription_not_billing` | upload | cust_00052 | sub_free_cust_00052 | $66.70 | $800.40 |
| `cancelled_subscription_still_billing` | upload | cust_00064 | sub_00064 | $4600.0000 | $55200.0000 |
| `missing_expected_invoice` | upload | cust_00062 | sub_00062 | $506.0000 | $6072.0000 |
| `credit_leakage` | upload | cust_00032 |, | $500.0000 | $0 |
| `duplicate_credit` | upload | cust_00085 |, | $50.0000 | $600.0000 |
| `duplicate_customer` | upload | cust_00032 |, | $0 | $0 |
| `currency_mismatch` | upload | cust_00069 | sub_00069 | $0 | $0 |
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

Upload validation blocks line items with missing invoice parents. Rule 25 is verified via harness using seed `3437452345`, not via CSV upload.
