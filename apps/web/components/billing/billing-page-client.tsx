"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";
import { ExternalLink } from "lucide-react";

import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { getBilling, getDashboard } from "@/lib/report-api";
import { ApiError } from "@/lib/api";
import type { BillingResponse } from "@rlr/shared";

export function BillingPageClient() {
  const router = useRouter();
  const { getToken, isSignedIn, isLoaded } = useAppAuth();
  const [billing, setBilling] = useState<BillingResponse | null>(null);
  const [pricingReportId, setPricingReportId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadBilling = useCallback(async () => {
    if (!isSignedIn) return;
    try {
      const token = await getToken();
      if (!token) return;
      const data = await getBilling(token);
      setBilling(data);
      setError(null);

      try {
        const dashboard = await getDashboard(token);
        const unpurchased = dashboard.audits.find((audit) => !audit.purchased);
        const latest = dashboard.audits[0];
        setPricingReportId(unpurchased?.report_id ?? latest?.report_id ?? null);
      } catch {
        setPricingReportId(null);
      }
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Unable to load billing information.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isSignedIn]);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in?redirect_url=/billing");
      return;
    }
    void loadBilling();
  }, [isLoaded, isSignedIn, loadBilling, router]);

  if (!isLoaded || isLoading) {
    return <PageLoadingSkeleton message="Loading billing…" />;
  }

  if (error && !billing) {
    return (
      <GlassCard padding="md" className="border-error/20 bg-error-bg text-center">
        <p className="text-body text-gray-700">{error}</p>
        <Button className="mt-6" onClick={() => void loadBilling()}>
          Retry
        </Button>
      </GlassCard>
    );
  }

  if (!billing) return null;

  const planLabel =
    billing.plan === "annual" ? "Annual Membership" : billing.plan === "none" ? "Pay per report" : billing.plan;

  return (
    <div className="mx-auto max-w-reading space-y-16 px-8 py-24">
      <div>
        <p className="text-overline uppercase text-gray-500">Account</p>
        <h1 className="mt-4 text-h1 text-primary">Billing</h1>
        <p className="mt-4 text-body text-gray-600">Manage your plan and report credits.</p>
      </div>

      <GlassCard padding="md">
        <div className="grid gap-6 sm:grid-cols-2">
          <div>
            <p className="text-caption text-gray-500">Current Plan</p>
            <p className="mt-2 text-h3 font-semibold text-gray-900">{planLabel}</p>
            <p className="mt-1 text-small capitalize text-gray-500">Status: {billing.status}</p>
          </div>
          <div>
            <p className="text-caption text-gray-500">Reports Remaining</p>
            <p className="mt-2 text-h3 font-semibold tabular-nums text-gray-900">
              {billing.reports_remaining}
            </p>
          </div>
        </div>

        {billing.plan !== "annual" && (
          <div className="mt-8 border-t border-border pt-8">
            <p className="text-body text-gray-600">
              Upgrade to annual membership for 12 detailed reports per year.
            </p>
            <Link
              href={
                pricingReportId ? `/pricing?report_id=${pricingReportId}` : "/pricing"
              }
              className="mt-4 inline-block"
            >
              <Button variant="secondary">View Annual Membership</Button>
            </Link>
          </div>
        )}

        {billing.portal_url && (
          <div className="mt-8">
            <a
              href={billing.portal_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-body text-primary hover:underline"
            >
              Manage subscription & receipts
              <ExternalLink className="h-4 w-4" strokeWidth={1.75} />
            </a>
          </div>
        )}
      </GlassCard>

      {billing.purchases.length > 0 && (
        <GlassCard padding="md">
          <h2 className="text-h3 font-semibold text-gray-900">Recent Purchases</h2>
          <ul className="mt-6 divide-y divide-border">
            {billing.purchases.map((purchase) => (
              <li
                key={`${purchase.report_id ?? "credit"}-${purchase.created_at}`}
                className="flex items-center justify-between py-4"
              >
                <div>
                  <p className="text-body text-gray-900 capitalize">{purchase.plan.replace(/_/g, " ")}</p>
                  <p className="text-small text-gray-500">
                    {purchase.created_at
                      ? new Date(purchase.created_at).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })
                      : "—"}
                  </p>
                </div>
                <div className="text-right">
                  {purchase.amount_cents != null && purchase.currency && (
                    <p className="text-body tabular-nums text-gray-900">
                      {new Intl.NumberFormat("en-US", {
                        style: "currency",
                        currency: purchase.currency.toUpperCase(),
                      }).format(purchase.amount_cents / 100)}
                    </p>
                  )}
                  {purchase.receipt_url && (
                    <a
                      href={purchase.receipt_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-small text-primary hover:underline"
                    >
                      Receipt
                    </a>
                  )}
                  {purchase.report_id ? (
                    <Link
                      href={`/report/${purchase.report_id}`}
                      className="mt-1 block text-small text-gray-500 hover:text-gray-900"
                    >
                      View report
                    </Link>
                  ) : (
                    <p className="mt-1 text-small text-gray-500">Report credit</p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </GlassCard>
      )}

      <Link href="/dashboard" className="text-small text-gray-500 underline-offset-4 hover:text-gray-900 hover:underline">
        ← Back to Dashboard
      </Link>
    </div>
  );
}
