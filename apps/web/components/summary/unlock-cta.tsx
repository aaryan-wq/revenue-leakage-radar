"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { CheckoutButton } from "@/components/summary/checkout-button";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { useAppAuth } from "@/lib/app-auth";
import { isClerkConfigured } from "@/lib/clerk";
import { getBilling, unlockWithCredit } from "@/lib/report-api";
import { getStoredAuditSession } from "@/lib/audit-session";

interface UnlockCtaProps {
  reportId: string;
  purchased: boolean;
  onUnlocked?: () => void;
}

export function UnlockCta({ reportId, purchased, onUnlocked }: UnlockCtaProps) {
  const { isSignedIn, getToken } = useAppAuth();
  const [reportsRemaining, setReportsRemaining] = useState(0);
  const [isUsingCredit, setIsUsingCredit] = useState(false);
  const [creditError, setCreditError] = useState<string | null>(null);

  useEffect(() => {
    if (!isSignedIn) return;
    void (async () => {
      const token = await getToken();
      if (!token) return;
      try {
        const billing = await getBilling(token);
        setReportsRemaining(billing.reports_remaining);
      } catch {
        setReportsRemaining(0);
      }
    })();
  }, [getToken, isSignedIn]);

  const handleUseCredit = async () => {
    setIsUsingCredit(true);
    setCreditError(null);
    try {
      const token = await getToken();
      if (!token) return;
      const session = getStoredAuditSession();
      await unlockWithCredit(reportId, token, session?.sessionToken);
      onUnlocked?.();
    } catch (err) {
      setCreditError(err instanceof Error ? err.message : "Unable to use credit.");
    } finally {
      setIsUsingCredit(false);
    }
  };

  if (purchased) {
    return (
      <GlassCard padding="lg" elevated className="text-center">
        <h3 className="text-h3 font-semibold text-gray-900">Full Report Unlocked</h3>
        <p className="mt-3 text-body text-gray-600">
          Your detailed evidence-backed report is ready to review.
        </p>
        <Link href={`/report/${reportId}`} className="mt-8 inline-block">
          <Button size="lg">View Full Report</Button>
        </Link>
      </GlassCard>
    );
  }

  return (
    <GlassCard padding="lg" elevated className="text-center">
      <h3 className="text-h3 font-semibold text-gray-900">Unlock Full Report</h3>
      <p className="mt-3 text-body text-gray-600">
        Get customer-level findings, invoice evidence, and remediation guidance.
      </p>

      {!isSignedIn ? (
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          {isClerkConfigured() ? (
            <Link href={`/sign-in?redirect_url=${encodeURIComponent("/summary")}`}>
              <Button size="lg" type="button">
                Sign In to Unlock
              </Button>
            </Link>
          ) : (
            <Button
              size="lg"
              disabled
              title="Add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY to .env to enable sign-in"
            >
              Sign In to Unlock
            </Button>
          )}
          <Link href={`/pricing?report_id=${reportId}`}>
            <Button variant="secondary" size="lg">
              View Pricing
            </Button>
          </Link>
        </div>
      ) : (
        <div className="mt-8 space-y-6">
          {reportsRemaining > 0 && (
            <div>
              <p className="mb-4 text-small text-gray-500">
                You have {reportsRemaining} report credit{reportsRemaining === 1 ? "" : "s"} remaining.
              </p>
              <Button size="lg" onClick={() => void handleUseCredit()} disabled={isUsingCredit}>
                {isUsingCredit ? "Unlocking…" : "Use 1 Credit"}
              </Button>
              {creditError && <p className="mt-2 text-caption text-error">{creditError}</p>}
            </div>
          )}
          <div className="flex flex-wrap items-center justify-center gap-4">
            <CheckoutButton
              reportId={reportId}
              plan="single_report"
              label="Purchase Report"
              onCreditUnlock={onUnlocked}
            />
            <CheckoutButton
              reportId={reportId}
              plan="annual_membership"
              label="Annual Membership"
              variant="secondary"
              onCreditUnlock={onUnlocked}
            />
            <Link href={`/pricing?report_id=${reportId}`}>
              <Button variant="ghost" size="lg">
                Compare Plans
              </Button>
            </Link>
          </div>
        </div>
      )}
    </GlassCard>
  );
}
