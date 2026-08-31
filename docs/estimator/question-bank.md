# Estimator Question Bank

Questionnaire version: **v2.3**

## Sections

| Section | Key questions | Branch triggers |
|---------|---------------|-----------------|
| profile | company_type, arr_amount, arr_confidence, customer_count | — |
| pricing | pricing.models (multiselect) | usage / per-seat sub-branches |
| usage | usage.rating, usage.reconciliation | `pricing.models` contains `usage` |
| seats | seats.reconciliation | `pricing.models` contains `per_seat` |
| product | billable_count, independent_catalogs, addons | — |
| contracts | negotiated_arr_pct, grandfathering, renewal_increases | — |
| discounts | frequency, auto_expiry_removal, expiry_confidence, stacking_policy | `auto_expiry_removal` when discounts are used |
| changes | pricing_changes_24mo, migration_method | — |
| systems | billing_system_count, primary_platform | — |
| operations | manual_override_frequency, unticketed_adjustments, credit_memo_process, churn_billing_cutoff | — |
| quote_to_bill | commercial_truth, quote_automation, finance_sales_disagreement | — |
| migrations | migrated_36mo | unlocks reconciliation + parallel_systems |
| international | multi_currency | unlocks currency_count |
| controls | billing_owner, monthly_reconciliation, billing_qa, invoice_price_qa | — |
| confidence | billing_confidence | — |

## Branching Rules

- `pricing.models` contains `usage` → usage section (2 questions)
- `pricing.models` contains `per_seat` → seats section (1 question)
- `migrations.migrated_36mo = true` → migration detail (2 questions)
- `international.multi_currency = true` → currency detail (1 question)
- `discounts.frequency` not `never` → `discounts.auto_expiry_removal`

## Question count

- Typical B2B SaaS path (flat pricing, no migration, single currency): **~33 questions**
- Full branched path (usage + seats + migration + multi-currency): **~39 questions**

## Answer Types

`select`, `multiselect`, `currency`, `number`, `scale`, `boolean`

## Unknown

Operational questions accept `unknown` as a valid answer. Unknown increases uncertainty; it is never treated as evidence of leakage.
