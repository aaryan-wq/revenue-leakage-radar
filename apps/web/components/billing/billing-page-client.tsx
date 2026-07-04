"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";
import { ExternalLink } from "lucide-react";

import { Reveal } from "@/components/motion";
import { LegalConsent } from "@/components/legal/legal-consent";
import { LegalLinks } from "@/components/legal/legal-links";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/hairline-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { useBillingQuery } from "@/lib/hooks/use-billing-query";
import { ApiError } from "@/lib/api";
import { planDisplayName, PRODUCT_NAMES } from "@/lib/pricing-content";

export function BillingPageClient() {
  const router = useRouter();
  const { isSignedIn, isLoaded } = useAppAuth();
  const billingQuery = useBillingQuery();

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in?redirect_url=/billing");
    }
  }, [isLoaded, isSignedIn, router]);

  const error =
    billingQuery.error instanceof ApiError
      ? billingQuery.error.message
      : billingQuery.error instanceof Error
        ? billingQuery.error.message
        : null;

  const billing = billingQuery.data ?? null;
  const isLoading = !isLoaded || (billingQuery.isLoading && !billing);

  if (isLoading) {
    return <PageLoadingSkeleton message="Loading billing…" variant="list" />;
  }

  if (error && !billing) {
    return (
      <HairlineCard padding="md" className="border-destructive/20 bg-destructive/5 text-center">
        <p className="text-muted-foreground">{error}</p>
        <Button className="mt-6" onClick={() => void billingQuery.refetch()}>
          Retry
        </Button>
      </HairlineCard>
    );
  }

  if (!billing) return null;

  const planLabel = planDisplayName(billing.plan);

  return (
    <div className="mx-auto max-w-marketing space-y-12 px-6 py-12 md:px-10">
      <Reveal>
        <div>
          <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">Account</p>
          <h1 className="mt-2 font-heading text-3xl tracking-tight">Billing</h1>
          <p className="mt-2 text-muted-foreground">Manage your plan and report credits.</p>
        </div>
      </Reveal>

      <Reveal delay={0.05}>
        <HairlineCard padding="md">
          <div className="grid gap-6 sm:grid-cols-2">
            <div>
              <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                Current plan
              </p>
              <p className="mt-2 font-heading text-2xl tracking-tight">{planLabel}</p>
              <p className="mt-1 text-sm capitalize text-muted-foreground">Status: {billing.status}</p>
            </div>
            <div>
              <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                Reports remaining
              </p>
              <p className="mt-2 font-heading text-2xl tracking-tight tnum">
                {billing.reports_remaining}
              </p>
            </div>
          </div>

          {billing.plan !== "annual" && (
            <div className="mt-8 border-t border-line pt-8">
              <p className="text-sm text-muted-foreground">
                Need recurring audits, integrations, or team workspace? Talk to us about{" "}
                {PRODUCT_NAMES.enterprise}.
              </p>
              <Link href="/contact" className="mt-4 inline-block">
                <Button variant="secondary">Contact Sales</Button>
              </Link>
            </div>
          )}

          {billing.portal_url && (
            <div className="mt-8">
              <a
                href={billing.portal_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
              >
                Manage subscription & receipts
                <ExternalLink className="h-4 w-4" strokeWidth={1.75} />
              </a>
            </div>
          )}
        </HairlineCard>
      </Reveal>

      {billing.purchases.length > 0 && (
        <Reveal delay={0.1}>
          <HairlineCard padding="md">
            <h2 className="font-heading text-xl tracking-tight">Recent purchases</h2>
            <ul className="mt-6 divide-y divide-line">
              {billing.purchases.map((purchase) => (
                <li
                  key={`${purchase.report_id ?? "credit"}-${purchase.created_at}`}
                  className="flex items-center justify-between gap-4 py-4"
                >
                  <div>
                    <p className="text-foreground">{planDisplayName(purchase.plan)}</p>
                    <p className="text-sm text-muted-foreground">
                      {purchase.created_at
                        ? new Date(purchase.created_at).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          })
                        : "-"}
                    </p>
                  </div>
                  <div className="text-right">
                    {purchase.amount_cents != null && purchase.currency && (
                      <p className="tnum text-foreground">
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
                        className="text-sm text-primary hover:underline"
                      >
                        Receipt
                      </a>
                    )}
                    {purchase.report_id ? (
                      <Link
                        href={`/report/${purchase.report_id}`}
                        className="mt-1 block text-sm text-muted-foreground hover:text-foreground"
                      >
                        View report
                      </Link>
                    ) : (
                      <p className="mt-1 text-sm text-muted-foreground">Report credit</p>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </HairlineCard>
        </Reveal>
      )}

      <Reveal delay={0.2}>
        <LegalConsent action="upgrading your plan" className="mt-4" />
        <LegalLinks className="mt-4" />
      </Reveal>

      <Link
        href="/dashboard"
        className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
      >
        ← Back to workspace
      </Link>
    </div>
  );
}
