"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Check } from "lucide-react";
import { AnalyticsEvents } from "@rlr/shared";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { PricingPageTracker } from "@/components/analytics/marketing-page-tracker";
import { LegalConsent } from "@/components/legal/legal-consent";
import { CheckoutButton } from "@/components/summary/checkout-button";
import { Button } from "@/components/ui/button";
import { useAppAuth } from "@/lib/app-auth";
import { isClerkConfigured } from "@/lib/clerk";
import { PRICING_TIERS, PRODUCT_NAMES } from "@/lib/pricing-content";
import { buildPricingSignInHref } from "@/lib/use-checkout-report";
import { captureEvent } from "@/lib/analytics/client";

function FeatureList({ items }: { items: string[] }) {
  return (
    <ul className="mb-8 mt-8 space-y-3">
      {items.map((item) => (
        <li key={item} className="flex items-start gap-3">
          <Check className="mt-0.5 h-4 w-4 shrink-0 text-foreground" strokeWidth={1.75} />
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
      className={`relative flex h-full flex-col rounded-xl bg-card p-8 ${
        highlighted ? "border-2 border-foreground" : "border border-line"
      }`}
    >
      {highlighted && (
        <span className="absolute -top-3 left-6 bg-foreground px-3 py-1 text-[0.65rem] uppercase tracking-widest text-primary-foreground">
          Most popular
        </span>
      )}
      <h2 className="min-h-16 font-heading text-xl leading-snug tracking-tight">{label}</h2>
      <div className="mt-4 flex min-h-20 items-end border-b border-line pb-6">
        <span
          className={`font-heading tracking-tight tnum ${
            compactPrice ? "text-2xl" : "text-4xl"
          }`}
        >
          {price}
        </span>
        {priceNote && (
          <span className="ml-2 text-sm text-muted-foreground">{priceNote}</span>
        )}
      </div>
      <p className="mt-4 min-h-24 text-sm leading-relaxed text-muted-foreground">{description}</p>
      <FeatureList items={features} />
      <div className="mt-auto">{cta}</div>
    </div>
  );
}

export function PricingPageClient() {
  const searchParams = useSearchParams();
  const urlReportId = searchParams.get("report_id");
  const { isSignedIn, isLoaded } = useAppAuth();
  const tiers = PRICING_TIERS;

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

    return (
      <CheckoutButton
        plan="single_report"
        label={tiers.verificationReport.cta}
        variant="primary"
        reportId={urlReportId}
      />
    );
  };

  return (
    <section className="border-t border-line">
      <PricingPageTracker />
      <div className="mx-auto max-w-marketing px-6 py-24 md:px-10 lg:py-32">
        <Reveal>
          <div className="mb-16 max-w-3xl">
            <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">Pricing</p>
            <h1 className="mt-6 font-heading text-[clamp(2.5rem,5vw,4rem)] leading-[1.05] tracking-tight text-balance">
              Start free. Buy the report when the evidence justifies it.
            </h1>
            <p className="mt-4 max-w-xl text-lg text-muted-foreground">
              Start with a free topline leakage scan. Unlock a {PRODUCT_NAMES.verificationReport}{" "}
              when you need evidence-backed findings and remediation guidance.
            </p>
          </div>
        </Reveal>

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

        <Reveal delay={0.15} className="mt-12 max-w-3xl">
          <LegalConsent action="purchasing a plan" className="text-center" />
        </Reveal>
      </div>
    </section>
  );
}
