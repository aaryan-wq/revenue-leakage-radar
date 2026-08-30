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
       → Percentiles (P10–P90)
       → Scenario bands + answer-aware insights
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

### Scenario Bands

Monte Carlo runs once per calculation. Scenarios select different percentile bands from the same simulation output:

| Scenario | Band | Use |
|----------|------|-----|
| Conservative | P10 to P50 | Lower plausible range |
| Expected (central) | P25 to P75 | Canonical headline range |
| Upside (aggressive) | P50 to P90 | Higher plausible range |

When the expected midpoint is positive but the lower band rounds to zero, the lower bound uses P10 so the headline does not read as "$0 to $X" without context.

### Insight Engine

After the model runs, a deterministic insight layer (no LLM math) produces:

- **Profile summary:** ARR, customer count, complexity label, and risk flags from your answers
- **Mechanism insights:** One sentence per top mechanism tying your specific answers to why it ranked
- **Verification preview:** Deterministic scan rules that would validate each top mechanism
- **Executive summary:** A short narrative using your numbers and top mechanisms

Optional AI narrative, when enabled, summarizes the result in prose. It never sets the numbers.

## What the Output Means

| Layer | Meaning |
|-------|---------|
| Expected value | Average across all 10,000 Monte Carlo runs (mean). This is the headline number. |
| Median run | P50 total. Often $0 when gaps appear in fewer than half of simulations. |
| Plausible range | Scenario percentile band (see Scenario Bands). May widen to P90 when P75 sits below the mean. |
| Expected (per mechanism) | Mean contribution for that mechanism across all runs |
| Detectable exposure | Portion likely identifiable from billing exports |
| Evidence required | Actual leakage requires the Paevo deterministic scan |

## Calibration Status

**Stage 1, fixture-calibrated model.** Monte Carlo intensity is tuned against five fictitious companies with bottom-up justified leakage (clean to very high complexity). Complexity score adjusts simulation intensity: low-complexity stacks receive a higher prior leakage rate; very high complexity stacks are dampened to respect overlap caps.

Stage 1 does not replace billing evidence. As completed audits accumulate, priors will continue to be updated with documented backtests.

## Limitations

- Self-reported inputs carry uncertainty
- Unknown answers widen intervals, never assume averages
- Model cannot identify specific customers or invoices
- Ranges reflect assumptions, not observed billing facts

## Verification

Replace assumptions with evidence: [Run a free deterministic scan](/upload).
