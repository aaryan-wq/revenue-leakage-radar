# How the SaaS Revenue Leakage Estimator Works

> **Disclaimer:** This is a modeled estimate based on self-reported billing characteristics. It is not a billing finding.

## What We Collect

Structured answers about ARR, pricing architecture, contracts, discounts, billing systems, manual operations, migrations, and organizational controls. No billing CSVs or integrations.

## Model Architecture

```
Answers → Normalize → Segment → Complexity score
       → H1–H18 posterior propensity scores
       → Per-hypothesis exposure (B × A × S × P × R × D)
       → Correlation overlap adjustment
       → Monte Carlo simulation (10,000 runs, seeded)
       → Percentiles (P10–P90; headline P25–P75)
```

### Exposure Formula (per hypothesis)

```
L_h = ExposureBase × AffectedRate × Severity × Persistence × Recoverability × Detectability
```

Different hypotheses use different exposure bases (full ARR, discount ARR, usage ARR, international ARR, etc.) to avoid double-counting the same revenue pool.

### Correlation

Hypothesis totals are **not** summed independently. Overlap penalties apply between correlated mechanisms (e.g., H1 ↔ H2, H3 ↔ H4).

### Complexity

A separate 0–40 score across pricing, contract, systems, change, and operations dimensions. Complexity modifies uncertainty and mechanism plausibility; it does not directly multiply ARR into leakage dollars.

## What the Output Means

| Layer | Meaning |
|-------|---------|
| Potential exposure | Revenue plausibly at risk under model assumptions |
| Detectable exposure | Portion likely identifiable from billing exports |
| Evidence required | Actual leakage requires the Paevo deterministic scan |

## Calibration Status

**Stage 0 — Structural model.** Not yet calibrated against a statistically representative audit dataset. As completed audits accumulate, priors will be updated with documented backtests.

## Limitations

- Self-reported inputs carry uncertainty
- Unknown answers widen intervals, never assume averages
- Model cannot identify specific customers or invoices
- Ranges reflect assumptions, not observed billing facts

## Verification

Replace assumptions with evidence: [Run a free deterministic scan](/upload).
