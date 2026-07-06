"use client";

import { useEffect } from "react";

import { useAppAuth } from "@/lib/app-auth";
import { ensureAuditLinked, getStoredAuditSession, setAuditAuthTokenProvider } from "@/lib/audit-session";

/** Wires Clerk auth into the audit funnel and links anonymous audits to signed-in accounts. */
export function AuditAuthBridge() {
  const { getToken, isLoaded, isSignedIn } = useAppAuth();

  useEffect(() => {
    setAuditAuthTokenProvider(getToken);
    return () => setAuditAuthTokenProvider(null);
  }, [getToken]);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    if (!getStoredAuditSession()) return;

    void (async () => {
      const token = await getToken();
      if (!token) return;
      await ensureAuditLinked(token);
    })();
  }, [getToken, isLoaded, isSignedIn]);

  return null;
}
