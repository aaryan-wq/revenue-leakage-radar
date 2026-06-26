"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Lock, Shield, Upload, Zap } from "lucide-react";

import { SiteFooter } from "@/components/marketing/site-footer";
import { GlassCard } from "@/components/ui/glass-card";
import { fadeUp, staggerContainer } from "@/lib/motion/variants";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";

const VERIFICATION_CHECKS = [
  { title: "Expired Discounts", description: "Coupons still applied after expiration date." },
  { title: "Legacy Pricing", description: "Subscriptions billed below current catalog rates." },
  { title: "Renewal Drift", description: "Renewal prices diverging from contract terms." },
  { title: "Duplicate Discounts", description: "Stacked discounts exceeding policy limits." },
  { title: "Price Catalog Mismatch", description: "Invoice line items not matching catalog." },
  { title: "Contract vs Billing", description: "CRM contract price differs from billed amount." },
];

const EXAMPLE_FINDINGS = [
  { customer: "Acme Corp", arr: "$48,000", category: "Legacy Pricing" },
  { customer: "Northwind LLC", arr: "$12,400", category: "Expired Discount" },
  { customer: "Globex Inc", arr: "$31,200", category: "Renewal Drift" },
];

const STEPS = [
  {
    icon: Upload,
    title: "Upload CSVs",
    description:
      "Export invoice line items and your price catalog — two files to start core pricing analysis.",
  },
  {
    icon: Zap,
    title: "Revenue Verification",
    description: "Deterministic rules scan subscriptions, invoices, and pricing for leakage.",
  },
  {
    icon: Shield,
    title: "Recover Revenue",
    description: "Get evidence-backed findings with estimated ARR impact and remediation steps.",
  },
];

function HeroUploadZone({ motionEnabled }: { motionEnabled: boolean }) {
  const router = useRouter();

  return (
    <motion.div
      role="button"
      tabIndex={0}
      onClick={() => router.push("/upload")}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") router.push("/upload");
      }}
      className="glass group mx-auto mt-12 flex min-h-[320px] max-w-2xl cursor-pointer flex-col items-center justify-center rounded-hero border-2 border-dashed border-border p-12 text-center transition-all duration-normal hover:border-blue hover:shadow-elevation-2 motion-safe-float"
      whileHover={motionEnabled ? { scale: 1.01 } : undefined}
      transition={{ duration: 0.2 }}
    >
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-surface-glass-subtle transition-colors group-hover:bg-blue-light">
        <Upload className="h-8 w-8 text-gray-500 transition-colors group-hover:text-blue" strokeWidth={1.75} />
      </div>
      <p className="text-h3 text-gray-900">Drop your billing CSVs here</p>
      <p className="mt-2 max-w-md text-small text-gray-500">
        Invoice line items and price catalog required. Start your free revenue scan in minutes.
      </p>
      <span className="mt-8 inline-flex h-10 items-center gap-2 rounded-button bg-primary px-6 text-small font-medium text-white transition-all group-hover:brightness-[1.04]">
        Browse Files
        <ArrowRight className="h-4 w-4" strokeWidth={1.75} />
      </span>
    </motion.div>
  );
}

export function LandingPageClient() {
  const motionEnabled = useMotionEnabled();

  const enterProps = motionEnabled
    ? { variants: staggerContainer, initial: "hidden" as const, animate: "visible" as const }
    : { initial: false as const };

  const scrollProps = motionEnabled
    ? {
        variants: staggerContainer,
        initial: "hidden" as const,
        whileInView: "visible" as const,
        viewport: { once: true, margin: "-80px" },
      }
    : { initial: false as const };

  const childVariants = motionEnabled ? fadeUp : undefined;

  return (
    <>
      <section className="relative overflow-hidden">
        <div className="mx-auto max-w-container px-8 pb-24 pt-20 md:pt-28">
          <motion.div className="mx-auto max-w-reading text-center" {...enterProps}>
            <motion.p variants={childVariants} className="text-overline uppercase text-gray-500">
              Revenue Verification for Finance Teams
            </motion.p>
            <motion.h1 variants={childVariants} className="mt-4 text-display-hero text-primary md:text-[4.5rem]">
              Find recoverable revenue in your billing data
            </motion.h1>
            <motion.p variants={childVariants} className="mt-6 text-large text-gray-500">
              Upload billing CSVs and receive a free Revenue Verification Summary in minutes.
              Deterministic checks. CFO-grade evidence.
            </motion.p>
            <motion.div variants={childVariants}>
              <HeroUploadZone motionEnabled={motionEnabled} />
            </motion.div>
            <motion.p variants={childVariants} className="mt-6 text-caption text-gray-400">
              No account required · Stripe, Chargebee, Maxio, Zuora exports supported
            </motion.p>
          </motion.div>
        </div>
      </section>

      <section className="mx-auto max-w-container px-8 py-24">
        <motion.div {...scrollProps}>
          <motion.h2 variants={childVariants} className="text-center text-h2 text-primary">
            How it works
          </motion.h2>
          <div className="mt-16 grid gap-8 md:grid-cols-3">
            {STEPS.map((step) => (
              <motion.div key={step.title} variants={childVariants}>
                <GlassCard interactive padding="md" className="h-full">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-glass-subtle">
                    <step.icon className="h-6 w-6 text-primary" strokeWidth={1.75} />
                  </div>
                  <h3 className="mt-6 text-h4 text-gray-900">{step.title}</h3>
                  <p className="mt-3 text-body text-gray-500">{step.description}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      <section className="border-y border-border">
        <div className="mx-auto max-w-container px-8 py-24">
          <motion.div className="text-center" {...scrollProps}>
            <motion.h2 variants={childVariants} className="text-h2 text-primary">
              Example Report Preview
            </motion.h2>
            <motion.p variants={childVariants} className="mx-auto mt-4 max-w-reading text-body text-gray-600">
              See the kind of recoverable ARR your finance team could act on.
            </motion.p>
            <motion.div variants={childVariants} className="mx-auto mt-12 max-w-reading">
              <GlassCard padding="md">
                <div className="space-y-4">
                  {EXAMPLE_FINDINGS.map((finding) => (
                    <div
                      key={finding.customer}
                      className="flex items-center justify-between border-b border-border pb-4 last:border-0 last:pb-0"
                    >
                      <div>
                        <p className="select-none text-body font-medium text-gray-400 blur-[3px]">
                          {finding.customer}
                        </p>
                        <p className="text-small text-gray-500">{finding.category}</p>
                      </div>
                      <p className="text-h4 font-semibold tabular-nums text-gray-900">{finding.arr}</p>
                    </div>
                  ))}
                </div>
                <p className="mt-8 text-center text-small text-gray-500">
                  Customer names blurred in free summary. Unlock for full evidence.
                </p>
              </GlassCard>
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section className="mx-auto max-w-container px-8 py-24">
        <motion.div {...scrollProps}>
          <motion.h2 variants={childVariants} className="text-center text-h2 text-primary">
            Verification Checks
          </motion.h2>
          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {VERIFICATION_CHECKS.map((check) => (
              <motion.div key={check.title} variants={childVariants}>
                <GlassCard padding="sm" className="h-full">
                  <h3 className="text-h4 text-gray-900">{check.title}</h3>
                  <p className="mt-2 text-body text-gray-500">{check.description}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      <section className="border-t border-border">
        <div className="mx-auto max-w-container px-8 py-24">
          <div className="grid gap-12 lg:grid-cols-2">
            <GlassCard padding="lg">
              <h2 className="text-h2 text-primary">Simple, transparent pricing</h2>
              <p className="mt-4 text-body text-gray-600">
                Start free. Purchase a detailed report when you need invoice-level evidence.
              </p>
              <ul className="mt-8 space-y-4 text-body text-gray-600">
                <li>Free — Revenue Verification Summary</li>
                <li>Detailed Report — One-time purchase per audit</li>
                <li>Annual Membership — 12 reports per year for teams</li>
              </ul>
              <Link href="/pricing" className="mt-8 inline-block">
                <span className="inline-flex h-12 items-center rounded-button bg-primary px-6 text-body font-medium text-white transition-all hover:brightness-[1.04] active:scale-[0.98]">
                  View Pricing
                </span>
              </Link>
            </GlassCard>
            <GlassCard padding="lg">
              <div className="flex items-center gap-3">
                <Lock className="h-6 w-6 text-primary" strokeWidth={1.75} />
                <h3 className="text-h3 font-semibold text-gray-900">Enterprise-grade security</h3>
              </div>
              <ul className="mt-6 space-y-3 text-body text-gray-600">
                <li>HTTPS encryption in transit</li>
                <li>Uploaded CSVs deleted after processing</li>
                <li>Provider-managed database encryption at rest</li>
              </ul>
              <Link
                href="/security"
                className="mt-6 inline-block text-body text-primary underline-offset-4 hover:underline"
              >
                Learn more about security →
              </Link>
            </GlassCard>
          </div>
        </div>
      </section>

      <SiteFooter />
    </>
  );
}
