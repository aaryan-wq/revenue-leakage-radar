"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Check } from "lucide-react";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { CheckoutButton } from "@/components/summary/checkout-button";
import { Button } from "@/components/ui/button";
import { useAppAuth } from "@/lib/app-auth";
import { isClerkConfigured } from "@/lib/clerk";
import { buildPricingSignInHref } from "@/lib/use-checkout-report";

const TIERS = {
  free: {
    label: "Free",
    price: "$0",
    priceNote: null as string | null,
    roi: "Identify recoverable revenue before you spend anything.",
    features: [
      "Free Revenue Verification Summary",
      "Estimated recoverable ARR",
      "Top leakage categories",
      "Coverage & confidence scores",
      "No account required",
    ],
  },
  single: {
    label: "Detailed Report",
    price: "$999",
    priceNote: "one-time",
    roi: "Most teams recover 10× the report cost in the first finding.",
    features: [
      "Customer-level findings",
      "Invoice evidence & remediation",
      "PDF & CSV export",
      "30-day report access",
      "Executive narrative",
    ],
  },
  annual: {
    label: "Annual Membership",
    price: "$7,500",
    priceNote: "/year",
    roi: "Best ROI for finance teams running quarterly revenue audits.",
    features: [
      "12 detailed reports per year",
      "Unlimited free summaries",
      "Historical comparisons",
      "Trend analysis",
      "Priority processing",
      "Team workspace",
    ],
  },
  enterprise: {
    label: "Enterprise",
    price: "Contact Sales",
    priceNote: null as string | null,
    roi: "For high-volume audits, multi-entity, and custom verification rules.",
    features: [
      "100+ audits/year or unlimited",
      "API integrations",
      "SSO & enterprise auth",
      "Multiple business entities",
      "Dedicated support",
      "Custom verification rules",
    ],
  },
} as const;

function FeatureList({ items }: { items: string[] }) {
  return (
    <ul className="mb-8 space-y-3">
      {items.map((item) => (
        <li key={item} className="flex items-start gap-3">
          <Check className="mt-0.5 h-4 w-4 shrink-0 text-foreground" strokeWidth={1.75} />
          <span className="text-sm text-muted-foreground">{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function PricingPageClient() {
  const searchParams = useSearchParams();
  const urlReportId = searchParams.get("report_id");
  const { isSignedIn, isLoaded } = useAppAuth();

  const renderPaidCta = (
    plan: "single_report" | "annual_membership",
    label: string,
    variant: "primary" | "secondary",
  ) => {
    if (!isLoaded) {
      return <div className="mt-6 h-14 animate-pulse rounded-full bg-secondary" />;
    }

    if (!isSignedIn) {
      if (!isClerkConfigured()) {
        return (
          <Link href="/sign-in" className="block">
            <Button className="w-full" size="lg" variant={variant === "secondary" ? "secondary" : "primary"}>
              Sign In to Purchase
            </Button>
          </Link>
        );
      }
      return (
        <Link href={buildPricingSignInHref(urlReportId)} className="block">
          <Button
            className="w-full"
            size="lg"
            type="button"
            variant={variant === "secondary" ? "secondary" : "primary"}
          >
            {label}
          </Button>
        </Link>
      );
    }

    return (
      <CheckoutButton plan={plan} label={label} variant={variant} reportId={urlReportId} />
    );
  };

  return (
    <section className="border-t border-line">
      <div className="mx-auto max-w-marketing px-6 py-24 md:px-10 lg:py-32">
        <Reveal>
          <div className="mb-16 max-w-3xl">
            <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">Pricing</p>
            <h1 className="mt-6 font-heading text-[clamp(2.5rem,5vw,4rem)] leading-[1.05] tracking-tight text-balance">
              Pay when the evidence justifies it.
            </h1>
            <p className="mt-4 max-w-xl text-lg text-muted-foreground">
              Start with a free summary. Unlock the detailed report when you are ready to act on
              customer-level evidence.
            </p>
          </div>
        </Reveal>

        <Stagger className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
          <StaggerItem>
            <div className="flex h-full flex-col rounded-xl border border-line bg-card p-8">
              <h2 className="font-heading text-xl tracking-tight">{TIERS.free.label}</h2>
              <div className="mt-4 border-b border-line pb-6">
                <span className="font-heading text-4xl tracking-tight tnum">{TIERS.free.price}</span>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">{TIERS.free.roi}</p>
              <FeatureList items={[...TIERS.free.features]} />
              <Link href="/upload" className="mt-auto block">
                <Button className="w-full" size="lg">
                  Run Free Audit →
                </Button>
              </Link>
            </div>
          </StaggerItem>

          <StaggerItem>
            <div className="flex h-full flex-col rounded-xl border border-line bg-card p-8">
              <h2 className="font-heading text-xl tracking-tight">{TIERS.single.label}</h2>
              <div className="mt-4 border-b border-line pb-6">
                <span className="font-heading text-4xl tracking-tight tnum">{TIERS.single.price}</span>
                {TIERS.single.priceNote && (
                  <span className="ml-2 text-sm text-muted-foreground">{TIERS.single.priceNote}</span>
                )}
              </div>
              <p className="mt-4 text-sm text-muted-foreground">{TIERS.single.roi}</p>
              <FeatureList items={[...TIERS.single.features]} />
              <div className="mt-auto">{renderPaidCta("single_report", "Purchase Report", "primary")}</div>
            </div>
          </StaggerItem>

          <StaggerItem>
            <div className="relative flex h-full flex-col rounded-xl border-2 border-foreground bg-card p-8">
              <span className="absolute -top-3 left-6 bg-foreground px-3 py-1 text-[0.65rem] uppercase tracking-widest text-primary-foreground">
                Best ROI
              </span>
              <h2 className="font-heading text-xl tracking-tight">{TIERS.annual.label}</h2>
              <div className="mt-4 border-b border-line pb-6">
                <span className="font-heading text-4xl tracking-tight tnum">{TIERS.annual.price}</span>
                {TIERS.annual.priceNote && (
                  <span className="ml-1 text-sm text-muted-foreground">{TIERS.annual.priceNote}</span>
                )}
              </div>
              <p className="mt-4 text-sm text-muted-foreground">{TIERS.annual.roi}</p>
              <FeatureList items={[...TIERS.annual.features]} />
              <div className="mt-auto">
                {renderPaidCta("annual_membership", "Get Annual Membership", "secondary")}
              </div>
            </div>
          </StaggerItem>

          <StaggerItem>
            <div className="flex h-full flex-col rounded-xl border border-line bg-card p-8">
              <h2 className="font-heading text-xl tracking-tight">{TIERS.enterprise.label}</h2>
              <div className="mt-4 border-b border-line pb-6">
                <span className="font-heading text-2xl tracking-tight">{TIERS.enterprise.price}</span>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">{TIERS.enterprise.roi}</p>
              <FeatureList items={[...TIERS.enterprise.features]} />
              <Link href="/contact" className="mt-auto block">
                <Button variant="secondary" className="w-full" size="lg">
                  Contact Sales
                </Button>
              </Link>
            </div>
          </StaggerItem>
        </Stagger>
      </div>
    </section>
  );
}
