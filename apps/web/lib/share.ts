import { formatCurrency } from "@rlr/shared";

export type ShareChannel = "linkedin" | "x" | "email";

/** Public landing page used in social posts (not the read-only assessment link). */
export const SOCIAL_SHARE_LANDING_PATH = "/";

export function buildSocialShareUrl(origin: string): string {
  const normalizedOrigin = origin.replace(/\/$/, "");
  return `${normalizedOrigin}${SOCIAL_SHARE_LANDING_PATH}`;
}

export function buildSocialShareText(estimateHigh: number): string {
  const amount = formatCurrency(estimateHigh);
  return `Just ran the numbers: we might be leaving ~${amount}/year on the table. If you're running finance or RevOps, Paevo has a free 5-minute calculator that might help figure out leakage. Worth a look.`;
}

export function buildSocialSharePost(estimateHigh: number, landingUrl: string): string {
  return `${buildSocialShareText(estimateHigh)}\n\n${landingUrl}`;
}

/** Read-only assessment link copy for email and internal sharing. */
export function buildTeamShareText(estimateHigh: number): string {
  return `We estimated ~${formatCurrency(estimateHigh)}/year in recoverable revenue leakage.`;
}

export function buildShareUrls(options: {
  origin: string;
  assessmentUrl?: string;
  estimateHigh: number;
}) {
  const { origin, assessmentUrl, estimateHigh } = options;
  const landingUrl = buildSocialShareUrl(origin);
  const socialPost = buildSocialSharePost(estimateHigh, landingUrl);
  const teamText = buildTeamShareText(estimateHigh);
  const subject = "Our revenue leakage estimate";
  const body = assessmentUrl
    ? `${teamText}\n\nView the breakdown: ${assessmentUrl}`
    : `${teamText}\n\nRun your own estimate: ${landingUrl}`;

  return {
    linkedin: `https://www.linkedin.com/feed/?shareActive=true&text=${encodeURIComponent(socialPost)}`,
    x: `https://x.com/intent/tweet?text=${encodeURIComponent(socialPost)}`,
    email: `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`,
  };
}

export function canNativeShare(): boolean {
  return typeof navigator !== "undefined" && typeof navigator.share === "function";
}

export async function shareNative(origin: string, estimateHigh: number): Promise<boolean> {
  if (!canNativeShare()) return false;

  const url = buildSocialShareUrl(origin);
  const text = buildSocialShareText(estimateHigh);

  try {
    await navigator.share({
      title: "Revenue leakage estimate",
      text,
      url,
    });
    return true;
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") return false;
    return false;
  }
}

export function openShareChannel(
  channel: ShareChannel,
  origin: string,
  estimateHigh: number,
  assessmentUrl?: string,
) {
  const urls = buildShareUrls({ origin, assessmentUrl, estimateHigh });
  if (channel === "email") {
    window.location.href = urls.email;
    return;
  }
  window.open(urls[channel], "_blank", "noopener,noreferrer");
}
