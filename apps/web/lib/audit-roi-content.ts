import {
  type AuditRoiMetrics,
  VALUATION_MULTIPLE_HIGH,
  VALUATION_MULTIPLE_LOW,
  VERIFICATION_REPORT_BASE_FEE_USD,
  formatCompactCurrency,
  formatCurrency,
  formatPaybackPeriod,
} from "@rlr/shared";

export const AUDIT_ROI_DISCLAIMER =
  "Illustrative estimate based on recoverable ARR from your free audit. Actual recovery depends on verification and collection.";

export const VALUATION_FRAMING =
  "For a SaaS company, every $1 of ARR can add $5 to $10+ to company valuation.";

export function formatRoiPercent(value: number): string {
  return `${Math.round(value).toLocaleString("en-US")}%`;
}

export function formatValuationRange(metrics: AuditRoiMetrics): string {
  return `${formatCompactCurrency(metrics.valuationUpliftLowUsd)} to ${formatCompactCurrency(metrics.valuationUpliftHighUsd)}`;
}

export function buildPositiveRoiHeadline(metrics: AuditRoiMetrics): string {
  const payback = formatPaybackPeriod(metrics);
  return payback ? `This audit pays for itself in ${payback}` : "This audit can pay for itself quickly";
}

export function buildPositiveRoiSubhead(recoverableArr: string): string {
  return `If you recover the ${formatCurrency(recoverableArr)} identified in your free audit`;
}

export function buildBelowBreakEvenHeadline(): string {
  return "Verify recovery before you invest";
}

export function buildBelowBreakEvenSubhead(): string {
  return "Your current recoverable ARR estimate is below the audit cost. Unlock the full report to verify whether additional recovery is available.";
}

export interface AuditRoiStat {
  label: string;
  value: string;
  detail?: string;
}

export function buildPositiveRoiStats(metrics: AuditRoiMetrics): AuditRoiStat[] {
  return [
    {
      label: "Net annual gain",
      value: `${formatCurrency(metrics.netAnnualGainUsd)}/yr`,
      detail: "After audit fees",
    },
    {
      label: "Return on investment",
      value: formatRoiPercent(metrics.roiPercent),
      detail: "Based on full identified recovery",
    },
    {
      label: "Base fee payback",
      value: `${metrics.baseFeePaybackPercent.toFixed(1)}%`,
      detail: "Of identified recovery covers the base fee",
    },
    {
      label: "Valuation uplift",
      value: formatValuationRange(metrics),
      detail: `At ${VALUATION_MULTIPLE_LOW}x to ${VALUATION_MULTIPLE_HIGH}x ARR`,
    },
  ];
}

export function buildGenericRoiStats(metrics: AuditRoiMetrics): AuditRoiStat[] {
  return buildPositiveRoiStats(metrics);
}

export function buildUnlockPaybackLine(metrics: AuditRoiMetrics): string {
  if (metrics.isPositiveRoi) {
    const payback = formatPaybackPeriod(metrics);
    if (payback) {
      return `Pays back in ${payback} if you recover the identified revenue.`;
    }
  }

  return `A ${formatCurrency(VERIFICATION_REPORT_BASE_FEE_USD)} audit pays for itself if it confirms about ${metrics.baseFeePaybackPercent.toFixed(1)}% of your identified recovery.`;
}
