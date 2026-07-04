# Verification Run, Seed 96845555

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
python scripts/verify_verification_dataset.py --seed 96845555
```

### 3. Regenerate this exact dataset

```bash
python scripts/generate_verification_dataset.py --seed 96845555 --customers 100
```

## Injected leakage (ground truth)

| Metric | Value |
|--------|-------|
| Monthly (injected) | $11781.1700 |
| Annual (injected) | $135374.0400 |
| Upload scan primary ARR | $128577.32 |

Verification-mode datasets use a **clean baseline** plus one injection per rule. Headline recoverable ARR in the app should be **close to** injected annual leakage (typically within ~15%), not millions from baseline noise.

## Per-rule expected leakage

| Rule | Channel | Customer | Subscription | Monthly | Annual |
|------|---------|----------|--------------|---------|--------|
| `legacy_pricing` | upload | cust_00008 | sub_00008 | $212.7000 | $2552.4000 |
| `price_catalog_mismatch` | upload | cust_00085 | sub_00085 | $38.6500 | $463.8000 |
| `grandfathered_pricing` | upload | cust_00093 | sub_00093 | $96.6000 | $1159.2000 |
| `missing_scheduled_increase` | upload | cust_00013 | sub_00013 | $64.4000 | $772.8000 |
| `renewal_price_drift` | upload | cust_00026 | sub_00026 | $136.9000 | $1642.8000 |
| `manual_price_override` | upload | cust_00057 | sub_00057 | $161.0000 | $1932.0000 |
| `incorrect_seat_price` | upload | cust_00078 | sub_00078 | $1368.5000 | $16422.0000 |
| `incorrect_addon_price` | upload | cust_00097 | sub_00097 | $9.6600 | $115.9200 |
| `expired_discount` | upload | cust_00017 | sub_00017 | $141.6800 | $1700.1600 |
| `discount_stacking` | upload | cust_00083 | sub_00083 | $183.0800 | $2196.9600 |
| `duplicate_discount` | upload | cust_00025 | sub_00025 | $64.4000 | $772.8000 |
| `permanent_promotional_discount` | upload | cust_00062 | sub_00062 | $0 | $0 |
| `excessive_discount` | upload | cust_00060 | sub_00060 | $10.0000 | $120.0000 |
| `discount_wrong_product` | upload | cust_00099 | sub_00099 | $114.4200 | $1373.0400 |
| `invoice_price_mismatch` | upload | cust_00019 | sub_00019 | $82.3800 | $988.5600 |
| `duplicate_subscription` | upload | cust_00023 | sub_dup_cust_00023_1 | $64.4000 | $772.8000 |
| `billing_frequency_mismatch` | upload | cust_00041 | sub_00041 | $0 | $0 |
| `active_subscription_not_billing` | upload | cust_00018 | sub_free_cust_00018 | $64.40 | $772.80 |
| `cancelled_subscription_still_billing` | upload | cust_00020 | sub_00020 | $5671.8000 | $68061.6000 |
| `missing_expected_invoice` | upload | cust_00043 | sub_00043 | $2746.2000 | $32954.4000 |
| `credit_leakage` | upload | cust_00065 |, | $500.0000 | $0 |
| `duplicate_credit` | upload | cust_00079 |, | $50.0000 | $600.0000 |
| `duplicate_customer` | upload | cust_00020 |, | $0 | $0 |
| `currency_mismatch` | upload | cust_00007 | sub_00007 | $0 | $0 |
| `orphaned_records` | harness only | cust_00001 |, | $0 | $0 |

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

## orphaned_records (rule 25)

Upload validation blocks line items with missing invoice parents. Rule 25 is verified via harness using seed `96845555`, not via CSV upload.
