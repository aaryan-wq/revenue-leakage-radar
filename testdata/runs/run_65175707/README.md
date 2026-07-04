# Verification Run, Seed 65175707

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
python scripts/verify_verification_dataset.py --seed 65175707
```

### 3. Regenerate this exact dataset

```bash
python scripts/generate_verification_dataset.py --seed 65175707 --customers 100
```

## Injected leakage (ground truth only)

| Metric | Value |
|--------|-------|
| Monthly | $10555.3733 |
| Annual | $120664.4796 |

These are the **24+1 intentional injections** only. The upload scan will show **much higher** headline ARR because the baseline company also triggers the same rules on other subscriptions.

## Per-rule expected leakage

| Rule | Channel | Customer | Subscription | Monthly | Annual |
|------|---------|----------|--------------|---------|--------|
| `legacy_pricing` | upload | cust_00077 | sub_00077 | $16.9633 | $203.5596 |
| `price_catalog_mismatch` | upload | cust_00080 | sub_00080 | $387.3800 | $4648.5600 |
| `grandfathered_pricing` | upload | cust_00040 | sub_00040 | $1660.0800 | $19920.9600 |
| `missing_scheduled_increase` | upload | cust_00007 | sub_00007 | $23.5700 | $282.8400 |
| `renewal_price_drift` | upload | cust_00044 | sub_00144 | $230.5500 | $2766.6000 |
| `manual_price_override` | upload | cust_00023 | sub_00023 | $1355.6200 | $16267.4400 |
| `incorrect_seat_price` | upload | cust_00079 | sub_00079 | $2357.5000 | $28290.0000 |
| `incorrect_addon_price` | upload | cust_00093 | sub_00093 | $8.4817 | $101.7804 |
| `expired_discount` | upload | cust_00026 | sub_00126 | $506.0000 | $6072.0000 |
| `discount_stacking` | upload | cust_00014 | sub_00114 | $195.5000 | $2346.0000 |
| `duplicate_discount` | upload | cust_00034 | sub_00134 | $287.5000 | $3450.0000 |
| `permanent_promotional_discount` | upload | cust_00037 | sub_00037 | $0 | $0 |
| `excessive_discount` | upload | cust_00064 | sub_00064 | $10.0000 | $120.0000 |
| `discount_wrong_product` | upload | cust_00031 | sub_00031 | $117.8700 | $1414.4400 |
| `invoice_price_mismatch` | upload | cust_00047 | sub_00147 | $141.4500 | $1697.4000 |
| `duplicate_subscription` | upload | cust_00039 | sub_dup_cust_00039_1 | $67.8500 | $814.2000 |
| `billing_frequency_mismatch` | upload | cust_00035 | sub_00135 | $0 | $0 |
| `active_subscription_not_billing` | upload | cust_00002 | sub_free_cust_00002 | $67.85 | $814.20 |
| `cancelled_subscription_still_billing` | upload | cust_00013 | sub_00113 | $961.2083 | $11534.4996 |
| `missing_expected_invoice` | upload | cust_00062 | sub_00062 | $1610.0000 | $19320.0000 |
| `credit_leakage` | upload | cust_00016 |, | $500.0000 | $0 |
| `duplicate_credit` | upload | cust_00083 |, | $50.0000 | $600.0000 |
| `duplicate_customer` | upload | cust_00022 |, | $0 | $0 |
| `currency_mismatch` | upload | cust_00078 | sub_00078 | $0 | $0 |
| `orphaned_records` | harness only | cust_00001 |, | $0 | $0 |

## Files

| File | Rows |
|------|------|
| customers.csv | 100 |
| subscriptions.csv | 153 |
| invoices.csv | 1763 |
| invoice_line_items.csv | 1758 |
| price_catalog.csv | 18 |
| coupons.csv | 3 |
| accounts.csv | 100 |
| contracts.csv | 2 |

## orphaned_records (rule 25)

Upload validation blocks line items with missing invoice parents. Rule 25 is verified via harness using seed `65175707`, not via CSV upload.
