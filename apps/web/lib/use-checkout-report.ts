export function buildPricingSignInHref(reportId: string | null): string {
  const redirectPath = reportId ? `/pricing?report_id=${reportId}` : "/pricing";
  return `/sign-in?redirect_url=${encodeURIComponent(redirectPath)}`;
}
