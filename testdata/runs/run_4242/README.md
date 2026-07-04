# Verification Run, Seed 4242

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
python scripts/verify_verification_dataset.py --seed 4242
```

### 3. Regenerate this exact dataset

```bash
python scripts/generate_verification_dataset.py --seed 4242 --customers 100
```

## Injected leakage (ground truth only)

| Metric | Value |
|--------|-------|
| Monthly | $14041.4700 |
| Annual | $162497.6400 |

These are the **24+1 intentional injections** only. The upload scan will show **much higher** headline ARR because the baseline company also triggers the same rules on other subscriptions.

## Per-rule expected leakage

| Rule | Channel | Customer | Subscription | Monthly | Annual |
|------|---------|----------|--------------|---------|--------|
| `legacy_pricing` | upload | cust_00014 | sub_00114 | $187.8800 | $2254.5600 |
| `price_catalog_mismatch` | upload | cust_00072 | sub_00072 | $1059.2500 | $12711.0000 |
| `grandfathered_pricing` | upload | cust_00049 | sub_00149 | $27.6000 | $331.2000 |
| `missing_scheduled_increase` | upload | cust_00044 | sub_00144 | $139.3800 | $1672.5600 |
| `renewal_price_drift` | upload | cust_00002 | sub_00102 | $136.6800 | $1640.1600 |
| `manual_price_override` | upload | cust_00048 | sub_00148 | $1626.1000 | $19513.2000 |
| `incorrect_seat_price` | upload | cust_00012 | sub_00112 | $4646.0000 | $55752.0000 |
| `incorrect_addon_price` | upload | cust_00071 | sub_00071 | $36.9200 | $443.0400 |
| `expired_discount` | upload | cust_00033 | sub_00033 | $110.4000 | $1324.8000 |
| `discount_stacking` | upload | cust_00077 | sub_00077 | $92.0000 | $1104.0000 |
| `duplicate_discount` | upload | cust_00064 | sub_00064 | $789.8200 | $9477.8400 |
| `permanent_promotional_discount` | upload | cust_00005 | sub_00105 | $0 | $0 |
| `excessive_discount` | upload | cust_00018 | sub_00018 | $10.0000 | $120.0000 |
| `discount_wrong_product` | upload | cust_00024 | sub_00024 | $232.3000 | $2787.6000 |
| `invoice_price_mismatch` | upload | cust_00097 | sub_00097 | $66.2400 | $794.8800 |
| `duplicate_subscription` | upload | cust_00055 | sub_dup_cust_00055_1 | $73.6000 | $883.2000 |
| `billing_frequency_mismatch` | upload | cust_00057 | sub_00057 | $0 | $0 |
| `active_subscription_not_billing` | upload | cust_00042 | sub_free_cust_00042 | $73.60 | $883.20 |
| `cancelled_subscription_still_billing` | upload | cust_00043 | sub_00043 | $1476.6000 | $17719.2000 |
| `missing_expected_invoice` | upload | cust_00007 | sub_00107 | $2707.1000 | $32485.2000 |
| `credit_leakage` | upload | cust_00022 |, | $500.0000 | $0 |
| `duplicate_credit` | upload | cust_00008 |, | $50.0000 | $600.0000 |
| `duplicate_customer` | upload | cust_00047 |, | $0 | $0 |
| `currency_mismatch` | upload | cust_00034 | sub_00034 | $0 | $0 |
| `orphaned_records` | harness only | cust_00001 |, | $0 | $0 |

## Files

| File | Rows |
|------|------|
| customers.csv | 100 |
| subscriptions.csv | 153 |
| invoices.csv | 1721 |
| invoice_line_items.csv | 1716 |
| price_catalog.csv | 18 |
| coupons.csv | 3 |
| accounts.csv | 100 |
| contracts.csv | 2 |

## orphaned_records (rule 25)

Upload validation blocks line items with missing invoice parents. Rule 25 is verified via harness using seed `4242`, not via CSV upload.
