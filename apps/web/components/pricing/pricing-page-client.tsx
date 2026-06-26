"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { Check } from "lucide-react";

import { CheckoutButton } from "@/components/summary/checkout-button";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { useAppAuth } from "@/lib/app-auth";
import { isClerkConfigured } from "@/lib/clerk";
import { fadeUp, staggerContainer } from "@/lib/motion/variants";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";
import { buildPricingSignInHref } from "@/lib/use-checkout-report";

const FEATURES = {
  free: [
    "Upload billing CSVs",
    "Revenue Verification Summary",
    "Estimated recoverable ARR",
    "Opportunity breakdown",
  ],
  single: [
    "Everything in Free Scan",
    "Customer-level findings",
    "Invoice-level evidence",
    "Remediation guidance",
    "PDF & CSV export",
  ],
  annual: [
    "Everything in Detailed Report",
    "12 reports per year",
    "Priority support",
    "Best for finance teams",
  ],
};

function FeatureList({ items }: { items: string[] }) {
  return (
    <ul className="mt-6 space-y-3 text-left">
      {items.map((item) => (
        <li key={item} className="flex items-start gap-3 text-body text-gray-600">
          <Check className="mt-0.5 h-5 w-5 shrink-0 text-success" strokeWidth={1.75} />
          {item}
        </li>
      ))}
    </ul>
  );
}

export function PricingPageClient() {
  const searchParams = useSearchParams();
  const urlReportId = searchParams.get("report_id");
  const { isSignedIn, isLoaded } = useAppAuth();
  const motionEnabled = useMotionEnabled();

  const enterProps = motionEnabled
    ? { variants: staggerContainer, initial: "hidden" as const, animate: "visible" as const }
    : { initial: false as const };

  const scrollProps = motionEnabled
    ? {
        variants: staggerContainer,
        initial: "hidden" as const,
        whileInView: "visible" as const,
        viewport: { once: true },
      }
    : { initial: false as const };

  const childVariants = motionEnabled ? fadeUp : undefined;

  const renderPaidCta = (
    plan: "single_report" | "annual_membership",
    label: string,
    helper: string,
    variant: "primary" | "secondary",
  ) => {
    if (!isLoaded) {
      return <div className="mt-8 h-12 animate-pulse rounded-lg bg-surface-glass-subtle" />;
    }

    if (!isSignedIn) {
      if (!isClerkConfigured()) {
        return (
          <div className="mt-8 space-y-3 text-center">
            <p className="text-caption text-gray-500">Sign-in is required to purchase.</p>
            <Link href="/sign-in" className="block">
              <Button className="w-full" size="lg" variant={variant === "secondary" ? "secondary" : "primary"}>
                Sign In
              </Button>
            </Link>
          </div>
        );
      }
      return (
        <div className="mt-8 space-y-3 text-center">
          <p className="text-caption text-gray-500">{helper}</p>
          <Link href={buildPricingSignInHref(urlReportId)} className="block">
            <Button
              className="w-full"
              size="lg"
              type="button"
              variant={variant === "secondary" ? "secondary" : "primary"}
            >
              {plan === "single_report" ? "Sign In to Purchase" : "Sign In to Subscribe"}
            </Button>
          </Link>
        </div>
      );
    }

    return (
      <div className="mt-8 space-y-3">
        <p className="text-caption text-center text-gray-500">{helper}</p>
        <CheckoutButton
          plan={plan}
          label={label}
          variant={variant}
          reportId={urlReportId}
        />
      </div>
    );
  };

  return (
    <div className="mx-auto max-w-container px-8 py-24">
      <motion.div className="mx-auto max-w-reading text-center" {...enterProps}>
        <motion.p variants={childVariants} className="text-overline uppercase text-gray-500">
          Pricing
        </motion.p>
        <motion.h1 variants={childVariants} className="mt-4 text-h1 text-primary">
          Simple, transparent pricing
        </motion.h1>
        <motion.p variants={childVariants} className="mt-4 text-body text-gray-600">
          Start with a free scan, or purchase now and apply credits when you upload billing data.
        </motion.p>
      </motion.div>

      <motion.div className="mt-16 grid gap-8 lg:grid-cols-3" {...scrollProps}>
        <motion.div variants={childVariants}>
          <GlassCard padding="md" className="h-full">
            <p className="text-overline uppercase text-gray-500">Free</p>
            <h2 className="mt-4 text-h2 font-semibold text-gray-900">$0</h2>
            <p className="mt-2 text-body text-gray-500">Revenue Verification Summary</p>
            <FeatureList items={FEATURES.free} />
            <Link href="/upload" className="mt-8 block">
              <Button variant="secondary" className="w-full" size="lg">
                Run Free Scan
              </Button>
            </Link>
          </GlassCard>
        </motion.div>

        <motion.div variants={childVariants}>
          <GlassCard padding="md" elevated className="h-full ring-2 ring-primary/20">
            <p className="text-overline uppercase text-primary">Most Popular</p>
            <h2 className="mt-4 text-h2 font-semibold text-gray-900">Detailed Report</h2>
            <p className="mt-2 text-body text-gray-500">One-time purchase per audit</p>
            <FeatureList items={FEATURES.single} />
            {renderPaidCta(
              "single_report",
              "Purchase Report",
              "Opens secure Stripe checkout. Adds one detailed report credit to your account.",
              "primary",
            )}
          </GlassCard>
        </motion.div>

        <motion.div variants={childVariants}>
          <GlassCard padding="md" className="h-full">
            <p className="text-overline uppercase text-gray-500">Teams</p>
            <h2 className="mt-4 text-h2 font-semibold text-gray-900">Annual Membership</h2>
            <p className="mt-2 text-body text-gray-500">12 detailed reports per year</p>
            <FeatureList items={FEATURES.annual} />
            {renderPaidCta(
              "annual_membership",
              "Get Annual Membership",
              "Opens secure Stripe checkout for annual membership (12 reports/year).",
              "secondary",
            )}
          </GlassCard>
        </motion.div>
      </motion.div>
    </div>
  );
}
