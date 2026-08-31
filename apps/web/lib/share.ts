import { formatCurrency } from "@rlr/shared";

export type ShareChannel = "linkedin" | "x" | "email";

export function buildEstimateShareText(estimateHigh: number): string {
  return `We estimated ~${formatCurrency(estimateHigh)}/year in recoverable revenue leakage.`;
}

export function buildShareUrls(url: string, estimateHigh: number) {
  const text = buildEstimateShareText(estimateHigh);
  const subject = "Revenue leakage estimate";
  const body = `${text}\n\nView the breakdown: ${url}`;

  return {
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
    x: `https://x.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`,
    email: `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`,
  };
}

export function canNativeShare(): boolean {
  return typeof navigator !== "undefined" && typeof navigator.share === "function";
}

export async function shareNative(url: string, estimateHigh: number): Promise<boolean> {
  if (!canNativeShare()) return false;

  try {
    await navigator.share({
      title: "Revenue leakage estimate",
      text: buildEstimateShareText(estimateHigh),
      url,
    });
    return true;
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") return false;
    return false;
  }
}

export function openShareChannel(channel: ShareChannel, url: string, estimateHigh: number) {
  const urls = buildShareUrls(url, estimateHigh);
  if (channel === "email") {
    window.location.href = urls.email;
    return;
  }
  window.open(urls[channel], "_blank", "noopener,noreferrer");
}
