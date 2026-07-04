export type Severity = 'critical' | 'elevated' | 'monitor'

export interface Finding {
  id: string
  title: string
  category: string
  annualized: number
  instances: number
  confidence: number
  severity: Severity
  detail: string
  evidence: { label: string; value: string }[]
  recovery: string
}

export const company = {
  name: 'Northwind Commerce',
  period: 'FY2025 · Jan–Dec',
  currency: 'USD',
  scope: '4.2M transactions · 11 systems reconciled',
}

export const totals = {
  recovered: 4_182_540,
  examined: 312_400_000,
  findings: 7,
  confidence: 0.94,
}

export const findings: Finding[] = [
  {
    id: 'F-01',
    title: 'Involuntary churn from failed card retries',
    category: 'Payments',
    annualized: 1_640_000,
    instances: 8_412,
    confidence: 0.97,
    severity: 'critical',
    detail:
      'Failed renewal charges are retried only twice before cancellation. A graduated retry schedule recovers the majority of these accounts within nine days.',
    evidence: [
      { label: 'Avg. recoverable rate', value: '71%' },
      { label: 'Median ticket', value: '$195 / mo' },
      { label: 'Window missed', value: 'Day 3–9' },
    ],
    recovery: 'Extend dunning to a 4-stage schedule with pre-expiry notice.',
  },
  {
    id: 'F-02',
    title: 'Discounts applied beyond approval policy',
    category: 'Pricing',
    annualized: 902_300,
    instances: 1_204,
    confidence: 0.93,
    severity: 'critical',
    detail:
      'Manual overrides exceeded the 15% discretionary ceiling on enterprise deals without secondary approval, eroding realized ARR.',
    evidence: [
      { label: 'Avg. over-discount', value: '9.4 pts' },
      { label: 'Deals affected', value: '1,204' },
      { label: 'Owner', value: 'Field Sales' },
    ],
    recovery: 'Enforce approval gates above threshold at quote generation.',
  },
  {
    id: 'F-03',
    title: 'Metered usage billed below recorded consumption',
    category: 'Billing',
    annualized: 740_900,
    instances: 22_870,
    confidence: 0.95,
    severity: 'elevated',
    detail:
      'A rounding rule truncated fractional usage units before invoicing, compounding across high-volume accounts.',
    evidence: [
      { label: 'Under-billed units', value: '1.9M' },
      { label: 'Accounts', value: '430' },
      { label: 'Drift', value: '0.6% / invoice' },
    ],
    recovery: 'Bill on raw metered units; reconcile the trailing 12 months.',
  },
  {
    id: 'F-04',
    title: 'Lapsed upgrades not enforced at renewal',
    category: 'Lifecycle',
    annualized: 488_200,
    instances: 612,
    confidence: 0.9,
    severity: 'elevated',
    detail:
      'Accounts that exceeded plan limits mid-term were not migrated to the correct tier at renewal, leaving value uncaptured.',
    evidence: [
      { label: 'Over-limit accounts', value: '612' },
      { label: 'Avg. uplift', value: '$640 / yr' },
      { label: 'Detection lag', value: '47 days' },
    ],
    recovery: 'Auto-propose tier change when usage exceeds limit for 30 days.',
  },
  {
    id: 'F-05',
    title: 'Currency conversion captured at stale rates',
    category: 'Finance',
    annualized: 214_640,
    instances: 5_980,
    confidence: 0.91,
    severity: 'monitor',
    detail:
      'Invoices in non-USD markets used a cached FX rate refreshed weekly, creating a systematic shortfall during volatility.',
    evidence: [
      { label: 'Markets', value: '6' },
      { label: 'Avg. spread', value: '1.3%' },
      { label: 'Refresh gap', value: '7 days' },
    ],
    recovery: 'Move to daily FX capture at invoice time.',
  },
  {
    id: 'F-06',
    title: 'Trial-to-paid conversions missing first charge',
    category: 'Payments',
    annualized: 132_500,
    instances: 1_870,
    confidence: 0.88,
    severity: 'monitor',
    detail:
      'A webhook race condition activated paid access before the initial charge settled, occasionally skipping it entirely.',
    evidence: [
      { label: 'Affected conversions', value: '1,870' },
      { label: 'Skipped charges', value: '0.9%' },
      { label: 'Avg. value', value: '$71' },
    ],
    recovery: 'Gate activation on settled payment confirmation.',
  },
  {
    id: 'F-07',
    title: 'Credits issued without offsetting reversal',
    category: 'Billing',
    annualized: 63_400,
    instances: 940,
    confidence: 0.86,
    severity: 'monitor',
    detail:
      'Goodwill credits were applied but the corresponding service was still delivered and never re-billed.',
    evidence: [
      { label: 'Credits issued', value: '940' },
      { label: 'Unreversed', value: '38%' },
      { label: 'Avg. credit', value: '$67' },
    ],
    recovery: 'Tie credit issuance to a tracked reversal workflow.',
  },
]

export const categories = [
  { name: 'Payments', amount: 1_772_500 },
  { name: 'Pricing', amount: 902_300 },
  { name: 'Billing', amount: 804_300 },
  { name: 'Lifecycle', amount: 488_200 },
  { name: 'Finance', amount: 214_640 },
]

export function formatCurrency(n: number, opts?: { compact?: boolean }) {
  if (opts?.compact) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(n)
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(n)
}
