# Verification Run, Seed 65420584

Fresh synthetic billing data with **one injected scenario per rule (25/25)**.

## Quick start

### 1. Upload test (25 rules via product UI)

Upload all 8 files from `upload/`:

- customers.csv, subscriptions.csv, invoices.csv, invoice_line_items.csv
- price_catalog.csv, coupons.csv, **accounts.csv**, **contracts.csv**

Start a **new audit** each time. Continue to validation → scan.

> Preview may show **22/25** rules before scan (credit/manual flags unknown pre-ingestion). After scan: **25/25** rules run and produce findings (including `orphaned_records` for line items with unresolved invoice parents).

### 2. Verify all 25 rules (engine)

```bash
python scripts/verify_verification_dataset.py --seed 65420584
```

Uses `harness/` CSVs (same data as upload) to validate **25/25** injected scenarios via the harness engine path.

### 3. Regenerate this exact dataset

```bash
python scripts/generate_verification_dataset.py --seed 65420584 --customers 100
```

## Injected leakage (ground truth)

| Metric | Value |
|--------|-------|
| Monthly (injected) | $10141.3600 |
| Annual (injected) | $115696.3200 |
| Upload scan primary ARR | $138388.04 |

Verification-mode datasets use a **clean baseline** plus one injection per rule. Headline recoverable ARR in the app should be **close to** injected annual leakage (typically within ~15%), not millions from baseline noise.

## Per-rule expected leakage

| Rule | Channel | Customer | Subscription | Monthly | Annual |
|------|---------|----------|--------------|---------|--------|
| `legacy_pricing` | upload | cust_00024 | sub_00024 | $287.7200 | $3452.6400 |
| `price_catalog_mismatch` | upload | cust_00038 | sub_00038 | $171.4900 | $2057.8800 |
| `grandfathered_pricing` | upload | cust_00074 | sub_00074 | $233.8800 | $2806.5600 |
| `missing_scheduled_increase` | upload | cust_00050 | sub_00050 | $142.8900 | $1714.6800 |
| `renewal_price_drift` | upload | cust_00075 | sub_00075 | $222.5700 | $2670.8400 |
| `manual_price_override` | upload | cust_00099 | sub_00099 | $741.7200 | $8900.6400 |
| `incorrect_seat_price` | upload | cust_00100 | sub_00100 | $4795.5000 | $57546.0000 |
| `incorrect_addon_price` | upload | cust_00051 | sub_00051 | $37.0900 | $445.0800 |
| `expired_discount` | upload | cust_00037 | sub_00037 | $109.7100 | $1316.5200 |
| `discount_stacking` | upload | cust_00001 | sub_00001 | $67.0500 | $804.6000 |
| `duplicate_discount` | upload | cust_00040 | sub_00040 | $239.7800 | $2877.3600 |
| `permanent_promotional_discount` | upload | cust_00011 | sub_00011 | $0 | $0 |
| `excessive_discount` | upload | cust_00086 | sub_00086 | $10.0000 | $120.0000 |
| `discount_wrong_product` | upload | cust_00002 | sub_00002 | $64.9700 | $779.6400 |
| `invoice_price_mismatch` | upload | cust_00041 | sub_00041 | $65.7900 | $789.4800 |
| `duplicate_subscription` | upload | cust_00083 | sub_dup_cust_00083_1 | $60.9500 | $731.4000 |
| `billing_frequency_mismatch` | upload | cust_00057 | sub_00057 | $0 | $0 |
| `active_subscription_not_billing` | upload | cust_00009 | sub_free_cust_00009 | $60.95 | $731.40 |
| `cancelled_subscription_still_billing` | upload | cust_00015 | sub_00015 | $1730.7500 | $20769.0000 |
| `missing_expected_invoice` | upload | cust_00077 | sub_00077 | $548.5500 | $6582.6000 |
| `credit_leakage` | upload | cust_00064 |, | $500.0000 | $0 |
| `duplicate_credit` | upload | cust_00043 |, | $50.0000 | $600.0000 |
| `duplicate_customer` | upload | cust_00081 |, | $0 | $0 |
| `currency_mismatch` | upload | cust_00063 | sub_00063 | $0 | $0 |
| `orphaned_records` | upload | cust_00001 |, | $0 | $0 |

## Files

| File | Rows |
|------|------|
| customers.csv | 100 |
| subscriptions.csv | 103 |
| invoices.csv | 2312 |
| invoice_line_items.csv | 2308 |
| price_catalog.csv | 10 |
| coupons.csv | 3 |
| accounts.csv | 3 |
| contracts.csv | 2 |

## harness/

Duplicate of `upload/` CSVs for harness-based engine verification (`verify_verification_dataset.py`).
