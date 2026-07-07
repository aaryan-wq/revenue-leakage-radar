"use client";

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { useAppAuth } from "@/lib/app-auth";
import {
  ensureAuditLinked,
  getAuditStatus,
  getStoredAuditSession,
  setAuditAuthTokenProvider,
} from "@/lib/audit-session";
import { queryKeys } from "@/lib/query/keys";

/** Wires Clerk auth into the audit funnel and links completed audits to signed-in accounts. */
export function AuditAuthBridge() {
  const queryClient = useQueryClient();
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
          const linked = await ensureAuditLinked(token);
          if (linked) {
            void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
          }
        }
      } catch {
        // Best effort — funnel pages will retry linking after scan completes.
      }
    })();
  }, [getToken, isLoaded, isSignedIn, queryClient]);

  return null;
}
