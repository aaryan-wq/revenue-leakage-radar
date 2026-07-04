import type { AnalyticsEventProperties } from "@rlr/shared";

const SESSION_KEY = "rlr_analytics_session";
const ANONYMOUS_USER_KEY = "rlr_anonymous_user_id";
const UTM_KEY = "rlr_utm";

type UtmParams = {
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
};

function randomId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function getSessionId(): string {
  if (typeof window === "undefined") return "server";
  let sessionId = sessionStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = randomId();
    sessionStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
}

export function getAnonymousUserId(): string {
  if (typeof window === "undefined") return "server";
  let anonymousId = localStorage.getItem(ANONYMOUS_USER_KEY);
  if (!anonymousId) {
    anonymousId = randomId();
    localStorage.setItem(ANONYMOUS_USER_KEY, anonymousId);
  }
  return anonymousId;
}

export function captureUtmFromSearch(search: string | URLSearchParams): void {
  if (typeof window === "undefined") return;
  const params = typeof search === "string" ? new URLSearchParams(search) : search;
  const utm: UtmParams = {
    utm_source: params.get("utm_source") ?? undefined,
    utm_medium: params.get("utm_medium") ?? undefined,
    utm_campaign: params.get("utm_campaign") ?? undefined,
  };
  if (utm.utm_source || utm.utm_medium || utm.utm_campaign) {
    localStorage.setItem(UTM_KEY, JSON.stringify(utm));
  }
}

function getStoredUtm(): UtmParams {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(UTM_KEY);
    return raw ? (JSON.parse(raw) as UtmParams) : {};
  } catch {
    return {};
  }
}

export function getDeviceType(): "desktop" | "tablet" | "mobile" {
  if (typeof window === "undefined") return "desktop";
  const width = window.innerWidth;
  if (width < 768) return "mobile";
  if (width < 1024) return "tablet";
  return "desktop";
}

export function getMarketingContext(): AnalyticsEventProperties {
  if (typeof window === "undefined") {
    return {};
  }

  return {
    session_id: getSessionId(),
    anonymous_user_id: getAnonymousUserId(),
    referrer: document.referrer || undefined,
    page_path: window.location.pathname,
    ...getStoredUtm(),
    device_type: getDeviceType(),
  };
}

export function getAuditContext(auditId?: string | null): AnalyticsEventProperties {
  return {
    ...getMarketingContext(),
    audit_id: auditId ?? undefined,
  };
}
