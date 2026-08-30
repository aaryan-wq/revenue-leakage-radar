# Paevo Revenue Leakage Estimator — Product Spec (Microtool)

> **Positioning:** Free marketing microtool on the public website. The CSV audit remains the main product.

## Purpose

The estimator answers: *Given the characteristics of your billing environment, how much revenue could plausibly be exposed to leakage?*

It does **not** answer: *How much revenue are you actually losing?* That requires billing evidence from the main Paevo scan.

## User Journey

```
Landing → Adaptive questionnaire → Monte Carlo model → Result → Run Free Scan (/upload)
```

## Non-Goals

- No billing data upload
- No account or email required before results
- No LLM financial calculations
- No fabricated industry benchmarks at launch
- Must not replace or compete with the main CSV audit product

## Output

1. Estimated annual/monthly leakage opportunity (P25–P75 range)
2. Conservative / central / high scenarios
3. Exposure by H1–H18 hypothesis mechanism
4. Complexity profile (separate from leakage)
5. Assumption ledger and methodology transparency
6. Handoff CTA to free deterministic scan

## Canonical Hypothesis Taxonomy (H1–H18)

| ID | Name |
|----|------|
| H1 | Grandfathered Pricing |
| H2 | Renewal Pricing Drift |
| H3 | Expired Discounts |
| H4 | Manual Discount Persistence |
| H5 | Product Catalog Drift |
| H6 | Price Version Mismatch |
| H7 | Product/SKU Mapping |
| H8 | Bundle Drift |
| H9 | Add-on Drift |
| H10 | Seat Pricing Drift |
| H11 | Usage Billing Drift |
| H12 | Quote vs Billing |
| H13 | Contract Configuration |
| H14 | Migration Errors |
| H15 | Multi-Currency Drift |
| H16 | Manual Billing Overrides |
| H17 | AI/Product Launch Drift |
| H18 | Enterprise Scaling |

## Model Maturity

Launch at **Stage 0: Structural model**. Priors are structural assumptions, not empirically calibrated industry facts.

## Related Docs

- [Model Methodology](estimator/model-methodology.md)
- [Question Bank](estimator/question-bank.md)
- [Hypothesis → Rule Mapping](estimator/hypothesis-rule-mapping.md)
- [Changelog](estimator/changelog.md)
- Main product: [product-spec.md](product-spec.md)
