import {
  INDUSTRY_LEAKAGE_PCT_AVERAGE,
  INDUSTRY_LEAKAGE_PCT_HIGH,
  INDUSTRY_LEAKAGE_PCT_LOW,
} from "@rlr/shared";

export const LANDING_ARR_MIN = 1_000_000;
export const LANDING_ARR_MAX = 100_000_000;
export const LANDING_ARR_DEFAULT = 12_000_000;

export interface LandingLeakageEstimate {
  arr: number;
  lowUsd: number;
  highUsd: number;
  centralUsd: number;
  headlineUsd: number;
  lowPct: number;
  highPct: number;
}

export function arrFromSliderPosition(position: number): number {
  const t = Math.min(1, Math.max(0, position));
  return Math.round(LANDING_ARR_MIN + t * (LANDING_ARR_MAX - LANDING_ARR_MIN));
}

export function sliderPositionFromArr(arr: number): number {
  const clamped = Math.min(LANDING_ARR_MAX, Math.max(LANDING_ARR_MIN, arr));
  return (clamped - LANDING_ARR_MIN) / (LANDING_ARR_MAX - LANDING_ARR_MIN);
}

/** Illustrative industry band: 3% to 5% of ARR, 4.2% average (survey benchmark, not audit). */
export function estimateLandingLeakage(arr: number): LandingLeakageEstimate {
  const lowPct = INDUSTRY_LEAKAGE_PCT_LOW;
  const highPct = INDUSTRY_LEAKAGE_PCT_HIGH;
  const lowUsd = Math.round(arr * lowPct);
  const highUsd = Math.round(arr * highPct);
  const headlineUsd = Math.round(arr * INDUSTRY_LEAKAGE_PCT_AVERAGE);
  const centralUsd = headlineUsd;

  return {
    arr,
    lowUsd,
    highUsd,
    centralUsd,
    headlineUsd,
    lowPct,
    highPct,
  };
}

export function formatArrLabel(arr: number): string {
  if (arr >= 1_000_000_000) {
    return `$${(arr / 1_000_000_000).toFixed(arr % 1_000_000_000 === 0 ? 0 : 1)}B`;
  }
  if (arr >= 1_000_000) {
    const millions = arr / 1_000_000;
    return `$${millions % 1 === 0 ? millions.toFixed(0) : millions.toFixed(1)}M`;
  }
  return `$${Math.round(arr / 1_000)}K`;
}
