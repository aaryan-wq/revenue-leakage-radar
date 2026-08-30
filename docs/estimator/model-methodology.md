# How the SaaS Revenue Leakage Estimator Works

> **Disclaimer:** This is a modeled estimate based on self-reported billing characteristics. It is not a billing finding.

## What We Collect

Structured answers about ARR, pricing architecture, contracts, discounts, billing systems, manual operations, migrations, and organizational controls. No billing CSVs or integrations.

## Model Architecture

```
Answers → Normalize (v2 segments) → Complexity score
       → 27 rule-native posterior scores
       → 27-stream Monte Carlo (10,000 runs, seeded)
       → Leak-family overlap adjustment
       → Aggregate to H1–H18 hypothesis rollups
       → Percentiles (P10–P90) + theoretical stack ceiling
       → Scenario bands + rule-aware insights
```

### Exposure Formula (per rule)

```
L_r = ExposureBase × AffectedRate × Severity × Persistence × Recoverability × ComplexityScale
```

Rules use dedicated exposure pools (discount ARR, usage ARR, billing execution ARR, credit ARR, etc.) to avoid double-counting the same revenue pool.

### Correlation

Rule totals are not summed independently. Overlap penalties apply within leak families (pricing gap, discount integrity, invoice execution, usage monetization, operational). Hypothesis totals are rollups of rule streams for executive UX.

### Complexity

A separate 0–40 score across pricing, contract, systems, change, and operations dimensions. Complexity modifies simulation intensity via `complexity_scale`. Tail fattening widens severity and persistence draws when billing confidence is low and complexity is high.

### Dual Headline Metrics

| Metric | Meaning |
|--------|---------|
| Expected recoverable | Overlap-adjusted mean across all runs (headline) |
| Stress case (P90) | Higher percentile total when mechanisms compound |
| Full rule ceiling | Sum of per-rule P90s before family overlap (transparency) |
| Recoverable slice | Expected weighted by rule recoverability |
| At-risk | Expected minus recoverable slice |

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

**Stage 2, rule-native model.** Monte Carlo uses 27 rule streams calibrated against verification fixture anchors and five fictitious audit personas. Complexity score and tail fattening adjust simulation intensity for low-confidence, high-complexity stacks.

Stage 2 does not replace billing evidence. As completed audits accumulate, priors will continue to be updated with documented backtests.

## Limitations

- Self-reported inputs carry uncertainty
- Unknown answers widen intervals, never assume averages
- Model cannot identify specific customers or invoices
- Ranges reflect assumptions, not observed billing facts

## Verification

Replace assumptions with evidence: [Run a free deterministic scan](/upload).
