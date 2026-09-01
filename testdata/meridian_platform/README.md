# Meridian Platform (fictional)

Synthetic billing export for a **~$27M ARR mid-market B2B SaaS** company (500 customers, hybrid per-seat + enterprise pricing).

Designed for **realistic** verification outcomes (~2.5 to 3.5% recoverable ARR), not stress-test noise.

## Files

| File | Description |
|------|-------------|
| `customers.csv` | 500 customers with Salesforce IDs |
| `subscriptions.csv` | 520 subscriptions (500 base + 20 migration duplicates) |
| `invoices.csv` | ~5,500 invoices (Jun 2023 to Aug 2025) |
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
python scripts/export_meridian_demo_fixture.py
```

Expected primary recoverable ARR: **~$750k to $900k** (~3% of $27M ARR), in line with the questionnaire calculator band.
