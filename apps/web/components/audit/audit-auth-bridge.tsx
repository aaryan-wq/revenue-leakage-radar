"use client";

import { useEffect } from "react";

import { useAppAuth } from "@/lib/app-auth";
import {
  ensureAuditLinked,
  getAuditStatus,
  getStoredAuditSession,
  setAuditAuthTokenProvider,
} from "@/lib/audit-session";

/** Wires Clerk auth into the audit funnel and links completed audits to signed-in accounts. */
export function AuditAuthBridge() {
  const { getToken, isLoaded, isSignedIn } = useAppAuth();

  useEffect(() => {
    setAuditAuthTokenProvider(getToken);
    return () => setAuditAuthTokenProvider(null);
  }, [getToken]);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    const session = getStoredAuditSession();
    if (!session) return;

    void (async () => {
      const token = await getToken();
      if (!token) return;

      try {
        const status = await getAuditStatus(session);
        if (status.status === "completed") {
          await ensureAuditLinked(token);
        }
      } catch {
        // Best effort — funnel pages will retry linking after scan completes.
      }
    })();
  }, [getToken, isLoaded, isSignedIn]);

  return null;
}
