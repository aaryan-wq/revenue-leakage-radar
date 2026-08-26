export const VERIFICATION_REPORT_BASE_FEE_USD = 2500;
export const SUCCESS_FEE_RATE = 0.1;

export interface CheckoutTotalBreakdown {
  baseFeeUsd: number;
  successFeeUsd: number;
  totalUsd: number;
}

export function computeCheckoutTotal(confirmedRecoveryUsd: number): CheckoutTotalBreakdown {
  const baseFeeUsd = VERIFICATION_REPORT_BASE_FEE_USD;
  const successFeeUsd = confirmedRecoveryUsd * SUCCESS_FEE_RATE;
  return {
    baseFeeUsd,
    successFeeUsd,
    totalUsd: baseFeeUsd + successFeeUsd,
  };
}

export function computeSuccessFeeCents(confirmedRecoveryUsd: number): number {
  return Math.round(confirmedRecoveryUsd * SUCCESS_FEE_RATE * 100);
}

export function parseUsdAmount(value: string | number): number {
  if (typeof value === "number") {
    return Number.isFinite(value) ? Math.max(0, value) : 0;
  }
  const parsed = Number.parseFloat(String(value).replace(/[^0-9.-]/g, ""));
  return Number.isFinite(parsed) ? Math.max(0, parsed) : 0;
}
