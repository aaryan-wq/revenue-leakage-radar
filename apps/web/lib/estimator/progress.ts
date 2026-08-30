/** Front-load perceived progress so early answers feel faster than the final stretch. */
export function easedCompletionPercent(completionRate: number): number {
  if (completionRate <= 0) return 0;
  if (completionRate >= 1) return 100;
  return Math.min(100, Math.pow(completionRate, 0.55) * 100);
}
