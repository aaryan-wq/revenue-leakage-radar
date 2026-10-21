"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Check } from "lucide-react";
import { AnalyticsEvents } from "@rlr/shared";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { PricingPageTracker } from "@/components/analytics/marketing-page-tracker";
import { AuditRoiSection } from "@/components/pricing/audit-roi-section";
import { LegalConsent } from "@/components/legal/legal-consent";
import { CheckoutButton } from "@/components/summary/checkout-button";
import { Button } from "@/components/ui/button";
import { useAppAuth } from "@/lib/app-auth";
import { isClerkConfigured } from "@/lib/clerk";
import { PRICING_TIERS, PRODUCT_NAMES } from "@/lib/pricing-content";
import { getReportFreeSummary } from "@/lib/report-api";
import { buildPricingSignInHref } from "@/lib/use-checkout-report";
import { captureEvent } from "@/lib/analytics/client";

function FeatureList({ items }: { items: string[] }) {
  return (
    <ul className="mb-8 mt-8 space-y-3">
      {items.map((item) => (
        <li key={item} className="flex items-start gap-3">
          <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" strokeWidth={1.75} />
          <span className="text-sm text-muted-foreground">{item}</span>
        </li>
      ))}
    </ul>
  );
}

function PricingCard({
  label,
  price,
  priceNote,
  compactPrice = false,
  description,
  features,
  cta,
  highlighted = false,
}: {
  label: string;
  price: string;
  priceNote?: string | null;
  compactPrice?: boolean;
  description: string;
  features: string[];
  cta: React.ReactNode;
  highlighted?: boolean;
}) {
  return (
    <div
      className={`relative flex h-full flex-col rounded-xl bg-card p-6 md:p-8 ${
        highlighted ? "border-2 border-primary" : "border border-line"
      }`}
    >
      {highlighted && (
        <span className="absolute -top-3 left-6 rounded-md bg-primary px-2 py-1 text-xs text-primary-foreground">
          Most popular
        </span>
      )}
      <h2 className="min-h-0 font-heading text-xl leading-snug tracking-tight md:min-h-16">{label}</h2>
      <div className="mt-4 flex min-h-0 items-end border-b border-line pb-5 md:min-h-20 md:pb-6">
        <span
          className={`font-heading tracking-tight tnum ${
            highlighted ? "text-primary" : ""
          } ${compactPrice ? "text-2xl" : "text-3xl md:text-4xl"}`}
        >
          {price}
        </span>
        {priceNote && (
          <span className="ml-2 text-sm text-muted-foreground">{priceNote}</span>
        )}
      </div>
      <p className="mt-4 min-h-0 text-sm leading-relaxed text-muted-foreground md:min-h-24">{description}</p>
      <FeatureList items={features} />
      <div className="mt-auto">{cta}</div>
    </div>
  );
}

export function PricingPageClient() {
  const searchParams = useSearchParams();
  const urlReportId = searchParams.get("report_id");
  const { isSignedIn, isLoaded, getToken } = useAppAuth();
  const [recoverableArr, setRecoverableArr] = useState<string | null>(null);
  const tiers = PRICING_TIERS;

  useEffect(() => {
    if (!isSignedIn || !urlReportId) {
      setRecoverableArr(null);
      return;
    }
    void (async () => {
      const token = await getToken();
      if (!token) return;
      try {
        const summary = await getReportFreeSummary(urlReportId, token);
        setRecoverableArr(summary.recoverable_arr);
      } catch {
        setRecoverableArr(null);
      }
    })();
  }, [getToken, isSignedIn, urlReportId]);

  const renderVerificationReportCta = () => {
    if (!isLoaded) {
      return <div className="mt-6 h-14 animate-pulse rounded-full bg-secondary" />;
    }

    if (!isSignedIn) {
      if (!isClerkConfigured()) {
        return (
          <Link href="/sign-in" className="block">
            <Button className="w-full" size="lg">
              Sign In to Unlock
            </Button>
          </Link>
        );
      }
      return (
        <Link href={buildPricingSignInHref(urlReportId)} className="block">
          <Button className="w-full" size="lg" type="button">
            {tiers.verificationReport.cta}
          </Button>
        </Link>
      );
    }

    if (!urlReportId || recoverableArr == null) {
      return (
        <Link href="/upload" className="block">
          <Button className="w-full" size="lg">
            Run Free Audit
          </Button>
        </Link>
      );
    }

    return (
      <CheckoutButton
        plan="single_report"
        label={tiers.verificationReport.cta}
        variant="primary"
        reportId={urlReportId}
        recoverableArr={recoverableArr}
      />
    );
  };

  return (
    <>
      <PricingPageTracker />
      <section className="bg-field">
        <div className="mx-auto max-w-marketing px-6 py-14 md:px-10 md:py-20">
          <Reveal>
            <div className="max-w-3xl">
              <h1 className="text-h1 text-balance text-foreground">
                Start free. Buy the report when the evidence justifies it.
              </h1>
              <p className="mt-4 max-w-xl text-base text-muted-foreground md:text-lg">
                Start with a free topline leakage scan. Unlock a {PRODUCT_NAMES.verificationReport}{" "}
                when you need evidence-backed findings and remediation guidance.
              </p>
            </div>
          </Reveal>
        </div>
      </section>
      <section>
      <div className="mx-auto max-w-marketing px-6 py-14 md:px-10 md:py-20">
        <Stagger className="grid items-stretch gap-4 lg:grid-cols-3">
          <StaggerItem className="h-full">
            <PricingCard
              label={tiers.free.label}
              price={tiers.free.price}
              description={tiers.free.description}
              features={[...tiers.free.features]}
              cta={
                <Link
                  href="/upload"
                  className="block"
                  onClick={() => captureEvent(AnalyticsEvents.FREE_AUDIT_CTA_CLICKED, { page_path: "/pricing" })}
                >
                  <Button className="w-full" size="lg">
                    {tiers.free.cta}
                  </Button>
                </Link>
              }
            />
          </StaggerItem>

          <StaggerItem className="h-full">
            <PricingCard
              label={tiers.verificationReport.label}
              price={tiers.verificationReport.price}
              priceNote={tiers.verificationReport.priceNote}
              compactPrice
              description={tiers.verificationReport.description}
              features={[...tiers.verificationReport.features]}
              highlighted
              cta={renderVerificationReportCta()}
            />
          </StaggerItem>

          <StaggerItem className="h-full">
            <PricingCard
              label={tiers.enterprise.label}
              price={tiers.enterprise.price}
              compactPrice
              description={tiers.enterprise.description}
              features={[...tiers.enterprise.features]}
              cta={
                <Link
                  href="/contact"
                  className="block"
                  onClick={() => captureEvent(AnalyticsEvents.ENTERPRISE_CTA_CLICKED, { page_path: "/pricing" })}
                >
                  <Button variant="secondary" className="w-full" size="lg">
                    {tiers.enterprise.cta}
                  </Button>
                </Link>
              }
            />
          </StaggerItem>
        </Stagger>

        <div className="mt-16 pt-4">
          <AuditRoiSection />
        </div>

        <Reveal delay={0.15} className="mt-12 max-w-3xl">
          <LegalConsent action="purchasing a plan" className="text-center" />
        </Reveal>
      </div>
      </section>
    </>
  );
}
