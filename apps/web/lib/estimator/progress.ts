/**
 * Front-load perceived progress so early answers move the bar a bit faster,
 * then gains taper as the assessment nears completion.
 *
 * Exponent < 1 maps linear completion to a concave curve (fast start, slow finish).
 */
export function easedCompletionPercent(completionRate: number): number {
  if (completionRate <= 0) return 0;
  if (completionRate >= 1) return 100;
  return Math.min(100, Math.pow(completionRate, 0.75) * 100);
}
