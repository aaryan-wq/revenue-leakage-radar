"use client";

import type { AnalyticsEventProperties } from "@rlr/shared";
import posthog from "posthog-js";

import { getAnonymousUserId, getMarketingContext } from "@/lib/analytics/context";
import {
  getLocalStorage,
  getPostHogPersistence,
  getSessionStorage,
  localStorageGetItem,
  localStorageSetItem,
} from "@/lib/browser-storage";

const POSTHOG_KEY_STORAGE = "rlr_posthog_project_key";

let initStarted = false;
let ready = false;
const pendingCaptures: Array<{ event: string; properties?: AnalyticsEventProperties }> = [];

function getApiKey(): string | undefined {
  return process.env.NEXT_PUBLIC_POSTHOG_KEY?.trim() || undefined;
}

function isEnabled(): boolean {
  return Boolean(getApiKey());
}

function clearStalePostHogPersistence(apiKey: string): void {
  if (typeof window === "undefined") return;

  const localStorage = getLocalStorage();
  const sessionStorage = getSessionStorage();
  if (!localStorage) return;

  const previousKey = localStorageGetItem(POSTHOG_KEY_STORAGE);
  if (previousKey && previousKey !== apiKey) {
    for (const storage of [localStorage, sessionStorage]) {
      if (!storage) continue;
      for (const key of [...Object.keys(storage)]) {
        if (key.startsWith("ph_") || key.includes("posthog")) {
          storage.removeItem(key);
        }
      }
    }
  }

  localStorageSetItem(POSTHOG_KEY_STORAGE, apiKey);
}

function flushPendingCaptures(): void {
  if (!ready) return;
  while (pendingCaptures.length > 0) {
    const next = pendingCaptures.shift();
    if (!next) break;
    posthog.capture(next.event, {
      ...getMarketingContext(),
      ...next.properties,
    });
  }
}

function markAnalyticsReady(): void {
  ready = true;
  if (process.env.NODE_ENV === "development") {
    posthog.debug(true);
  }
  identifyAnonymous();
  flushPendingCaptures();
}

function isHeadInitQueued(): boolean {
  const queued = posthog as typeof posthog & { _i?: unknown[] };
  return Array.isArray(queued._i) && queued._i.length > 0;
}

function waitForHeadInit(): void {
  if (posthog.__loaded) {
    markAnalyticsReady();
    return;
  }

  const startedAt = Date.now();
  const poll = () => {
    if (posthog.__loaded) {
      markAnalyticsReady();
      return;
    }

    if (Date.now() - startedAt > 10_000) {
      if (process.env.NODE_ENV === "development") {
        console.warn("[analytics] PostHog head script did not finish loading within 10s.");
      }
      return;
    }

    window.setTimeout(poll, 50);
  };

  poll();
}

export function initAnalytics(): void {
  if (initStarted || typeof window === "undefined") return;

  const apiKey = getApiKey();
  if (!apiKey) {
    initStarted = true;
    if (process.env.NODE_ENV === "development") {
      console.warn(
        "[analytics] PostHog disabled: NEXT_PUBLIC_POSTHOG_KEY missing from client bundle. " +
          "Set it in apps/web/.env.local and restart `npm run dev`.",
      );
    }
    return;
  }

  initStarted = true;
  clearStalePostHogPersistence(apiKey);

  if (process.env.NODE_ENV === "development") {
    console.info(`[analytics] PostHog project key loaded: ${apiKey.slice(0, 12)}…`);
  }

  if (posthog.__loaded || isHeadInitQueued()) {
    waitForHeadInit();
    return;
  }

  posthog.init(apiKey, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST ?? "https://d.paevo.co",
    ui_host: process.env.NEXT_PUBLIC_POSTHOG_UI_HOST ?? "https://us.posthog.com",
    defaults: "2026-05-30",
    capture_pageview: false,
    capture_pageleave: false,
    persistence: getPostHogPersistence(),
    person_profiles: "identified_only",
    advanced_disable_flags: true,
    disable_surveys: true,
    loaded: () => {
      markAnalyticsReady();
    },
  });
}

export function identifyAnonymous(): void {
  if (!isEnabled() || !ready) return;
  posthog.identify(getAnonymousUserId());
}

export function identifyUser(userId: string, traits?: Record<string, string | number | boolean>): void {
  if (!isEnabled()) return;
  initAnalytics();
  if (!ready) return;
  posthog.identify(userId, traits);
}

export function resetAnalyticsIdentity(): void {
  if (!isEnabled() || !ready) return;
  posthog.reset();
  identifyAnonymous();
}

export function captureEvent(
  event: string,
  properties?: AnalyticsEventProperties,
): void {
  if (!isEnabled()) return;
  initAnalytics();

  if (!ready) {
    pendingCaptures.push({ event, properties });
    return;
  }

  posthog.capture(event, {
    ...getMarketingContext(),
    ...properties,
  });
}

export function captureAuditEvent(
  event: string,
  auditId: string,
  properties?: AnalyticsEventProperties,
): void {
  captureEvent(event, {
    audit_id: auditId,
    ...properties,
  });
}
