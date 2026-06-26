"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";

import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { Skeleton } from "@/components/ui/skeleton";
import { getCheckoutStatus } from "@/lib/report-api";

const PAID_STATUSES = new Set(["paid", "no_payment_required"]);

export function CheckoutSuccessClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { getToken, isSignedIn, isLoaded } = useAppAuth();
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [reportId, setReportId] = useState<string | null>(null);

  const sessionId = searchParams.get("session_id");

  const pollStatus = useCallback(async () => {
    if (!sessionId || !isSignedIn) return;
    const token = await getToken();
    if (!token) return;

    try {
      const result = await getCheckoutStatus(sessionId, token);
      if (result.report_id) {
        setReportId(result.report_id);
      }
      if (
        PAID_STATUSES.has(result.payment_status) &&
        result.fulfilled
      ) {
        setStatus("ready");
        router.replace("/dashboard?checkout=success");
      }
    } catch {
      setStatus("error");
    }
  }, [getToken, isSignedIn, router, sessionId]);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      const redirectTarget = sessionId
        ? `/checkout/success?session_id=${encodeURIComponent(sessionId)}`
        : "/checkout/success";
      router.replace(`/sign-in?redirect_url=${encodeURIComponent(redirectTarget)}`);
      return;
    }
    if (!sessionId) {
      setStatus("error");
      return;
    }

    void pollStatus();
    const interval = setInterval(() => void pollStatus(), 2000);
    const timeout = setTimeout(() => setStatus("error"), 30000);
    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [isLoaded, isSignedIn, pollStatus, router, sessionId]);

  if (status === "error") {
    return (
      <div className="mx-auto max-w-reading px-8 py-24">
        <GlassCard padding="lg" elevated className="text-center">
          <h1 className="text-h2 text-primary">Payment Processing</h1>
          <p className="mt-4 text-body text-gray-600">
            Your payment may still be processing. Check your dashboard in a moment.
          </p>
          <div className="mt-8 flex justify-center gap-4">
            <Link href="/dashboard">
              <Button>Go to Dashboard</Button>
            </Link>
            {reportId && (
              <Link href={`/report/${reportId}`}>
                <Button variant="secondary">View Report</Button>
              </Link>
            )}
          </div>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-reading px-8 py-24 text-center">
      <Skeleton className="mx-auto h-8 w-8 rounded-full" />
      <h1 className="mt-6 text-h2 text-primary">Updating your account…</h1>
      <p className="mt-4 text-body text-gray-600">
        Payment received. We are applying your purchase to your account.
      </p>
    </div>
  );
}
