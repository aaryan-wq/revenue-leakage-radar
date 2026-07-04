"use client";

import { useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";

import { captureUtmFromSearch } from "@/lib/analytics/context";
import {
  identifyAnonymous,
  identifyUser,
  initAnalytics,
  resetAnalyticsIdentity,
} from "@/lib/analytics/client";

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const searchParams = useSearchParams();
  const { isSignedIn, userId, isLoaded } = useAuth();
  const wasSignedInRef = useRef(false);

  useEffect(() => {
    initAnalytics();
    captureUtmFromSearch(searchParams);
  }, [searchParams]);

  useEffect(() => {
    if (!isLoaded) return;

    if (isSignedIn && userId) {
      identifyUser(userId);
      wasSignedInRef.current = true;
      return;
    }

    if (wasSignedInRef.current) {
      resetAnalyticsIdentity();
      wasSignedInRef.current = false;
      return;
    }

    identifyAnonymous();
  }, [isLoaded, isSignedIn, userId]);

  return children;
}
