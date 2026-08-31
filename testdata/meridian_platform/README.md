# Meridian Platform (fictional)

Synthetic billing export for a **~$24M ARR mid-market B2B SaaS** company (450 customers, hybrid per-seat + enterprise pricing).

Designed for **realistic** verification outcomes (~3 to 6% recoverable ARR), not stress-test noise.

## Files

| File | Description |
|------|-------------|
| `customers.csv` | 450 customers with Salesforce IDs |
| `subscriptions.csv` | 470 subscriptions (450 base + 20 migration duplicates) |
| `invoices.csv` | ~5,000 invoices (Jun 2023 to Aug 2025) |
| `invoice_line_items.csv` | One line item per invoice, USD only |
| `price_catalog.csv` | v1/v2 USD catalog |
| `coupons.csv` | EOY25, PARTNER15 |
| `crm_accounts.csv` | Seat counts aligned to max active subscription quantity |
| `crm_contracts.csv` | Contracts for grandfathered undercharge scenarios |

## Injected scenarios (23 leaky subscriptions)

| Scenario | Count |
|----------|------:|
| Expired discount still applied | 6 |
| Legacy pricing after catalog v2 | 3 |
| Duplicate discount stacking | 3 |
| Grandfathered undercharging | 6 |
| Canceled sub still billing | 2 |
| Invoice price mismatch | 5 |
| Manual price override | 4 |
| Migration duplicate subs | 20 customers |

## Commands

```bash
python scripts/generate_meridian_dataset.py
python scripts/verify_meridian_dataset.py
```

Expected primary recoverable ARR: **~$550k to $750k** (~2 to 3% of ARR), in line with the questionnaire calculator band.
