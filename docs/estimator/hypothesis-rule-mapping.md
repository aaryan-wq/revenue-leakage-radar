# H1–H18 → Verification Rule Mapping

Maps estimator hypothesis buckets to deterministic verification rules in the main audit product. Used for scan handoff personalization only; does not suppress rules.

| Hypothesis | Verification rule IDs |
|------------|----------------------|
| H1 Grandfathered Pricing | `grandfathered_pricing`, `legacy_pricing` |
| H2 Renewal Pricing Drift | `renewal_price_drift`, `missing_scheduled_increase` |
| H3 Expired Discounts | `expired_discount` |
| H4 Manual Discount Persistence | `permanent_promotional_discount`, `manual_price_override` |
| H5 Product Catalog Drift | `price_catalog_mismatch` |
| H6 Price Version Mismatch | `legacy_pricing`, `price_catalog_mismatch` |
| H7 Product/SKU Mapping | `incorrect_addon_price`, `price_catalog_mismatch` |
| H8 Bundle Drift | `incorrect_addon_price`, `discount_wrong_product` |
| H9 Add-on Drift | `incorrect_addon_price` |
| H10 Seat Pricing Drift | `incorrect_seat_price` |
| H11 Usage Billing Drift | *(partial coverage; extend rules later)* |
| H12 Quote vs Billing | `contract_billing_price_divergence` |
| H13 Contract Configuration | `contract_billing_price_divergence`, `billing_frequency_mismatch` |
| H14 Migration Errors | `orphaned_records`, `duplicate_subscription` |
| H15 Multi-Currency Drift | `currency_mismatch` |
| H16 Manual Billing Overrides | `manual_price_override` |
| H17 AI/Product Launch Drift | `price_catalog_mismatch`, `legacy_pricing` |
| H18 Enterprise Scaling | composite: contract + seat + discount rules |

Machine-readable copy: [`packages/estimator-schema/hypothesis-rule-map.json`](../../packages/estimator-schema/hypothesis-rule-map.json)
