# Estimator Question Bank

Questionnaire version: **v2.1**

## Sections

| Section | Key questions | Branch triggers |
|---------|---------------|-----------------|
| profile | company_type, arr, arr_confidence, customers | — |
| pricing | pricing_models (multi), usage_based, seat_based | usage/seat sub-branches |
| usage | unit_type, rating, billing_timing, reconciliation | `pricing.usage_based = true` |
| seats | seat_reconciliation, true_up | `pricing.seat_based = true` |
| product | billable_products, independent_catalogs, addons | — |
| contracts | negotiated_arr_pct, custom_pricing, grandfathering, renewal_increases | — |
| discounts | discount_frequency, discount_types, expiry_handling, expiry_confidence, stacking_policy | — |
| changes | pricing_changes_24mo, migration_method, grandfathered_after_change | — |
| systems | billing_system_count, primary_platform | — |
| operations | manual_override_frequency, manual_change_logging, credit_memo_process, churn_billing_cutoff, invoice_cadence, customer_dedup | — |
| quote_to_bill | commercial_truth_source, quote_automation | — |
| migrations | migrated_36mo | unlocks migration detail |
| international | multi_currency | unlocks currency detail |
| controls | finance_team_size, billing_owner, reconciliation, billing_qa, invoice_price_qa | — |
| velocity | commercial_changes_12mo | — |
| confidence | billing_confidence, last_reconciliation | — |

## Branching Rules

- `pricing.usage_based = true` → usage section (6 questions)
- `pricing.seat_based = true` → seats section (4 questions)
- `migrations.migrated_36mo = true` → migration detail (3 questions)
- `international.multi_currency = true` → currency detail (2 questions)

## Answer Types

`select`, `multiselect`, `currency`, `number`, `scale`, `boolean`

## Unknown

Operational questions accept `unknown` as a valid answer. Unknown increases uncertainty; it is never treated as evidence of leakage.
