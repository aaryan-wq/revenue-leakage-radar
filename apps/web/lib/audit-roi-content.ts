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

export function buildPricingRoiHeadline(metrics: AuditRoiMetrics): string {
  const payback = formatPaybackPeriod(metrics);
  return payback
    ? `Verified recovery often pays back in ${payback}`
    : "Verified recovery often pays back quickly";
}

export function buildPricingRoiSubhead(): string {
  return `Most finance teams recover more than the report cost on the first verified finding. With a ${formatCurrency(VERIFICATION_REPORT_BASE_FEE_USD)} base fee plus 10% of confirmed recovery, recurring revenue you recapture compounds into cash flow and enterprise value.`;
}

export const PRICING_ROI_DISCLAIMER =
  "Illustrative example. Actual ROI depends on how much revenue you verify and recover.";

export function buildPricingRoiStats(metrics: AuditRoiMetrics): AuditRoiStat[] {
  return [
    {
      label: "Example net gain",
      value: `${formatCurrency(metrics.netAnnualGainUsd)}/yr`,
      detail: "After audit fees at $50K recovered ARR",
    },
    {
      label: "Example ROI",
      value: formatRoiPercent(metrics.roiPercent),
      detail: "When recovery exceeds total report cost",
    },
    {
      label: "Base fee threshold",
      value: `${metrics.baseFeePaybackPercent.toFixed(1)}%`,
      detail: "Of recovered ARR covers the base fee alone",
    },
    {
      label: "Valuation uplift",
      value: formatValuationRange(metrics),
      detail: `At ${VALUATION_MULTIPLE_LOW}x to ${VALUATION_MULTIPLE_HIGH}x ARR`,
    },
  ];
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

export function buildEstimatorRoiHeadline(metrics: AuditRoiMetrics): string {
  const payback = formatPaybackPeriod(metrics);
  return payback
    ? `If this estimate holds, the audit pays back in ${payback}`
    : "If this estimate holds, the audit can pay back quickly";
}

export function buildEstimatorRoiSubhead(estimateHighUsd: number): string {
  return `Based on ~${formatCurrency(estimateHighUsd)}/year recoverable from your assessment. A free billing scan verifies the number before you invest in the full report.`;
}

export const ESTIMATOR_ROI_DISCLAIMER =
  "Illustrative ROI from your questionnaire estimate, not billing records. Actual recovery depends on verification and collection.";

export function buildEstimatorBelowBreakEvenSubhead(): string {
  return "Your current estimate is below the audit cost. A free billing scan may surface additional recovery worth verifying.";
}

export function buildEstimatorRoiStats(metrics: AuditRoiMetrics): AuditRoiStat[] {
  return [
    {
      label: "Net annual gain",
      value: `${formatCurrency(metrics.netAnnualGainUsd)}/yr`,
      detail: "If the high estimate is confirmed and recovered",
    },
    {
      label: "Return on investment",
      value: formatRoiPercent(metrics.roiPercent),
      detail: "After base fee and 10% success fee",
    },
    {
      label: "Base fee payback",
      value: `${metrics.baseFeePaybackPercent.toFixed(1)}%`,
      detail: "Of confirmed recovery covers the base fee",
    },
    {
      label: "Valuation uplift",
      value: formatValuationRange(metrics),
      detail: `At ${VALUATION_MULTIPLE_LOW}x to ${VALUATION_MULTIPLE_HIGH}x ARR`,
    },
  ];
}

export function buildEstimatorCtaPaybackLine(metrics: AuditRoiMetrics): string {
  if (metrics.isPositiveRoi) {
    const payback = formatPaybackPeriod(metrics);
    if (payback) {
      return `At this estimate, a verified audit pays back in ${payback}.`;
    }
  }

  return `A ${formatCurrency(VERIFICATION_REPORT_BASE_FEE_USD)} audit pays for itself if billing data confirms about ${metrics.baseFeePaybackPercent.toFixed(1)}% of this estimate.`;
}
