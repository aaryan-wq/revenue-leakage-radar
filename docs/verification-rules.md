# Verification Rules v2.0 (25 Deterministic Rules)

Production verification engine rules. All rules:

- Run on canonical entities only
- Use the shared financial calculator (`verification/calculator/financial.py`)
- Emit structured `calculation_trace` evidence
- Skip automatically when required fields are missing

## Pricing (8)

| Rule ID | Name |
|---------|------|
| `legacy_pricing` | Legacy Pricing |
| `price_catalog_mismatch` | Price Catalog Mismatch |
| `grandfathered_pricing` | Grandfathered Pricing |
| `missing_scheduled_increase` | Missing Scheduled Increase |
| `renewal_price_drift` | Renewal Price Drift |
| `manual_price_override` | Manual Price Override |
| `incorrect_seat_price` | Incorrect Seat Price |
| `incorrect_addon_price` | Incorrect Add-on Price |

## Discounts (6)

| Rule ID | Name |
|---------|------|
| `expired_discount` | Expired Discount |
| `discount_stacking` | Discount Stacking |
| `duplicate_discount` | Duplicate Discount |
| `permanent_promotional_discount` | Permanent Promotional Discount |
| `excessive_discount` | Excessive Discount |
| `discount_wrong_product` | Discount Applied to Wrong Product |

## Billing (6)

| Rule ID | Name |
|---------|------|
| `invoice_price_mismatch` | Invoice Price Mismatch |
| `duplicate_subscription` | Duplicate Subscription |
| `billing_frequency_mismatch` | Billing Frequency Mismatch |
| `active_subscription_not_billing` | Active Subscription Not Billing |
| `cancelled_subscription_still_billing` | Cancelled Subscription Still Billing |
| `missing_expected_invoice` | Missing Expected Invoice |

## Credits (2)

| Rule ID | Name |
|---------|------|
| `credit_leakage` | Credit Leakage |
| `duplicate_credit` | Duplicate Credit |

## Data Quality (3)

| Rule ID | Name |
|---------|------|
| `duplicate_customer` | Duplicate Customer |
| `currency_mismatch` | Currency Mismatch |
| `orphaned_records` | Orphaned Records |

## Finding Contract

Every finding includes:

- `rule_id`, `rule_name`, `severity`, `confidence`, `status`
- `expected_value`, `actual_value`, `difference`
- `estimated_monthly_loss`, `estimated_arr_loss`
- `calculation_trace` (step-by-step reproducible math)
- `evidence` (canonical ID references)
- `finding_ref` (deterministic hash)

## Engine Layers

```
CanonicalContext → Rule Eligibility → Rule Modules → Shared Calculator → Finding Generator → Attribution
```

AI may narrate findings after generation. AI never computes financial values.
