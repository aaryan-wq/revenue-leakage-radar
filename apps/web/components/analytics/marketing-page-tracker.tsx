"use client";

import { AnalyticsEvents } from "@rlr/shared";

import { useTrackPageView } from "@/lib/analytics/hooks";

export function MarketingPageTracker({ event }: { event: string }) {
  useTrackPageView(event);
  return null;
}

export const LandingPageTracker = () => (
  <MarketingPageTracker event={AnalyticsEvents.LANDING_PAGE_VIEWED} />
);

export const PricingPageTracker = () => (
  <MarketingPageTracker event={AnalyticsEvents.PRICING_PAGE_VIEWED} />
);

export const SecurityPageTracker = () => (
  <MarketingPageTracker event={AnalyticsEvents.SECURITY_PAGE_VIEWED} />
);

export const FaqPageTracker = () => (
  <MarketingPageTracker event={AnalyticsEvents.FAQ_PAGE_VIEWED} />
);
