import {
  VERIFICATION_REPORT_BASE_FEE_USD,
  computeCheckoutTotal,
  parseUsdAmount,
} from "./pricing";

export const VALUATION_MULTIPLE_LOW = 5;
export const VALUATION_MULTIPLE_HIGH = 10;

/** Break-even recoverable ARR when full recovery is confirmed: 0.9R = base fee. */
export const AUDIT_ROI_BREAK_EVEN_ARR_USD =
  VERIFICATION_REPORT_BASE_FEE_USD / (1 - 0.1);

export const GENERIC_ROI_EXAMPLE_ARR_USD = 50_000;

export interface AuditRoiMetrics {
  recoverableArrUsd: number;
  baseFeeUsd: number;
  successFeeUsd: number;
  totalCostUsd: number;
  netAnnualGainUsd: number;
  roiPercent: number;
  paybackDays: number | null;
  paybackMonths: number | null;
  baseFeePaybackPercent: number;
  valuationUpliftLowUsd: number;
  valuationUpliftHighUsd: number;
  isPositiveRoi: boolean;
}

export function computeAuditRoi(recoverableArrUsd: number): AuditRoiMetrics | null {
  const recoverable = Math.max(0, recoverableArrUsd);
  if (recoverable <= 0) {
    return null;
  }

  const { baseFeeUsd, successFeeUsd, totalUsd } = computeCheckoutTotal(recoverable);
  const netAnnualGainUsd = recoverable - totalUsd;
  const isPositiveRoi = netAnnualGainUsd > 0;
  const roiPercent = totalUsd > 0 ? (netAnnualGainUsd / totalUsd) * 100 : 0;

  const dailyRecovery = recoverable / 365;
  const paybackDays = dailyRecovery > 0 ? totalUsd / dailyRecovery : null;
  const monthlyRecovery = recoverable / 12;
  const paybackMonths = monthlyRecovery > 0 ? totalUsd / monthlyRecovery : null;

  const baseFeePaybackPercent = (baseFeeUsd / recoverable) * 100;

  return {
    recoverableArrUsd: recoverable,
    baseFeeUsd,
    successFeeUsd,
    totalCostUsd: totalUsd,
    netAnnualGainUsd,
    roiPercent,
    paybackDays,
    paybackMonths,
    baseFeePaybackPercent,
    valuationUpliftLowUsd: recoverable * VALUATION_MULTIPLE_LOW,
    valuationUpliftHighUsd: recoverable * VALUATION_MULTIPLE_HIGH,
    isPositiveRoi,
  };
}

export function computeAuditRoiFromAmount(value: string | number): AuditRoiMetrics | null {
  return computeAuditRoi(parseUsdAmount(value));
}

export function formatPaybackPeriod(metrics: AuditRoiMetrics): string {
  if (!metrics.isPositiveRoi || metrics.paybackDays == null) {
    return "";
  }

  if (metrics.paybackDays < 60) {
    const days = Math.round(metrics.paybackDays);
    return days === 1 ? "1 day" : `${days} days`;
  }

  if (metrics.paybackMonths != null && metrics.paybackMonths < 24) {
    const months = Math.round(metrics.paybackMonths * 10) / 10;
    return months === 1 ? "1 month" : `${months} months`;
  }

  const years = Math.round((metrics.paybackDays / 365) * 10) / 10;
  return years === 1 ? "1 year" : `${years} years`;
}

export function formatCompactCurrency(value: number): string {
  if (value >= 1_000_000) {
    const decimals = value >= 10_000_000 ? 0 : 1;
    return `$${(value / 1_000_000).toFixed(decimals)}M`;
  }
  if (value >= 1_000) {
    const decimals = value >= 10_000 ? 0 : 1;
    return `$${(value / 1_000).toFixed(decimals)}K`;
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}
