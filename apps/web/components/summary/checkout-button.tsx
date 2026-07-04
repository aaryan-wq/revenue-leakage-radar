"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { AnalyticsEvents } from "@rlr/shared";

import { Button } from "@/components/ui/button";
import { useAppAuth } from "@/lib/app-auth";
import { getStoredAuditSession } from "@/lib/audit-session";
import { captureAuditEvent } from "@/lib/analytics/client";
import { createCheckout } from "@/lib/report-api";
import type { CheckoutPlan } from "@rlr/shared";

interface CheckoutButtonProps {
  plan: CheckoutPlan;
  label: string;
  reportId?: string | null;
  variant?: "primary" | "secondary";
  onCreditUnlock?: () => void;
}

export function CheckoutButton({
  reportId,
  plan,
  label,
  variant = "primary",
}: CheckoutButtonProps) {
  const { getToken, isSignedIn } = useAppAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClick = async () => {
    if (!isSignedIn) return;
    setIsLoading(true);
    setError(null);
    try {
      const token = await getToken();
      if (!token) {
        setError("Authentication required.");
        return;
      }

      const session = getStoredAuditSession();
      if (session?.auditId) {
        if (reportId) {
          captureAuditEvent(AnalyticsEvents.REPORT_UNLOCK_CTA_CLICKED, session.auditId, {
            checkout_type: plan,
          });
        }
        captureAuditEvent(AnalyticsEvents.CHECKOUT_STARTED, session.auditId, {
          checkout_type: plan,
          payment_provider: "stripe",
        });
      }
      const { checkout_url } = await createCheckout(
        plan,
        token,
        reportId,
        session?.sessionToken,
      );
      if (!checkout_url) {
        setError("Unable to start checkout.");
        if (session?.auditId) {
          captureAuditEvent(AnalyticsEvents.CHECKOUT_FAILED, session.auditId, {
            checkout_type: plan,
          });
        }
        return;
      }
      window.location.href = checkout_url;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Checkout failed.";
      setError(message);
      const session = getStoredAuditSession();
      if (session?.auditId) {
        captureAuditEvent(AnalyticsEvents.CHECKOUT_FAILED, session.auditId, {
          checkout_type: plan,
          error: message,
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <Button
        size="lg"
        variant={variant === "secondary" ? "secondary" : "primary"}
        onClick={() => void handleClick()}
        disabled={!isSignedIn || isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" strokeWidth={1.75} />
            Processing…
          </>
        ) : (
          label
        )}
      </Button>
      {error && <p className="text-sm text-leak">{error}</p>}
    </div>
  );
}
