"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

import { captureEvent } from "@/lib/analytics/client";
import { getDeviceType, getMarketingContext, getSessionId } from "@/lib/analytics/context";

const trackedPages = new Set<string>();

export function useTrackPageView(eventName: string, enabled = true): void {
  const pathname = usePathname();
  const trackedRef = useRef<string | null>(null);

  useEffect(() => {
    if (!enabled) return;

    const pageKey = `${eventName}:${pathname}`;
    if (trackedRef.current === pageKey || trackedPages.has(pageKey)) {
      return;
    }

    trackedRef.current = pageKey;
    trackedPages.add(pageKey);

    captureEvent(eventName, {
      ...getMarketingContext(),
      session_id: getSessionId(),
      page_path: pathname,
      device_type: getDeviceType(),
    });
  }, [enabled, eventName, pathname]);
}

export function useTrackOnce(
  eventName: string,
  properties?: Record<string, string | number | boolean | null | undefined>,
  enabled = true,
): void {
  const firedRef = useRef(false);
  const propertiesKey = JSON.stringify(properties ?? {});

  useEffect(() => {
    if (!enabled || firedRef.current) return;
    firedRef.current = true;

    captureEvent(eventName, {
      ...getMarketingContext(),
      session_id: getSessionId(),
      device_type: getDeviceType(),
      ...properties,
    });
  }, [enabled, eventName, propertiesKey, properties]);
}
