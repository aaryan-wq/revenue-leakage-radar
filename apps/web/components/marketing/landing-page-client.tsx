"use client";

import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { motion } from "framer-motion";

import { CountUp } from "@/components/count-up";
import { glide, Reveal, Stagger, StaggerItem } from "@/components/motion";
import { ArrLeakageHero } from "@/components/marketing/arr-leakage-hero";
import { AnalyticsEvents } from "@rlr/shared";
import { captureEvent } from "@/lib/analytics/client";
import { FreeReportPreview } from "@/components/marketing/free-report-preview";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { SecuritySummary } from "@/components/marketing/security-summary";
import { ViewSampleReportCta } from "@/components/marketing/view-sample-report-cta";
import { LandingPageTracker } from "@/components/analytics/marketing-page-tracker";
import { SiteFooter } from "@/components/site-footer";
import { VERIFICATION_RULE_COUNT } from "@/lib/verification-rules";

const STATS = [
  { value: 8, prefix: "", suffix: "", decimals: 0, label: "Billing & CRM platforms supported" },
  { value: 4, prefix: "", suffix: "", decimals: 0, label: "Data coverage tiers" },
  { value: 94, prefix: "", suffix: "%", decimals: 0, label: "Median finding confidence" },
  { value: 100, prefix: "", suffix: "%", decimals: 0, label: "Deterministic financial math" },
];

const METHOD_STEPS = [
  {
    n: "01",
    title: "Reconcile",
    body: "We ingest billing and CRM exports from your payment processor, ledger, and sales systems, then align every transaction across systems. No integration required.",
  },
  {
    n: "02",
    title: "Detect",
    body: "Each revenue path is examined against its intended behavior. Where reality diverges from policy, we measure the gap and annualize the impact.",
  },
  {
    n: "03",
    title: "Present",
    body: "Findings arrive as a board-ready report: ranked by recoverable dollars, supported by evidence, and paired with a precise remedy.",
  },
];

function HeroUploadZone() {
  const router = useRouter();
  const [hover, setHover] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const goToUpload = useCallback(() => {
    captureEvent(AnalyticsEvents.FREE_AUDIT_CTA_CLICKED, { source: "landing_upload_zone" });
    router.push("/upload");
  }, [router]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragActive(false);
      setHover(false);
      goToUpload();
    },
    [goToUpload],
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1, ease: glide, delay: 0.2 }}
      className="flex flex-col gap-4"
    >
      <motion.div
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") goToUpload();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
          setHover(true);
        }}
        onDragEnter={() => {
          setDragActive(true);
          setHover(true);
        }}
        onDragLeave={() => {
          setDragActive(false);
          setHover(false);
        }}
        onDrop={handleDrop}
        onClick={goToUpload}
        animate={{ scale: dragActive ? 1.008 : 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 24 }}
        className="relative cursor-pointer overflow-hidden rounded-2xl border-2 border-dashed border-line bg-card transition-colors duration-300 hover:border-primary/40"
      >
        <motion.div
          className="pointer-events-none absolute inset-0"
          animate={{ opacity: hover ? 1 : 0 }}
          transition={{ duration: 0.5 }}
          style={{
            background:
              "radial-gradient(110% 80% at 50% 0%, color-mix(in oklch, var(--primary) 6%, transparent), transparent 60%)",
          }}
        />

        <div className="relative flex flex-col items-center px-5 py-10 text-center sm:px-8 sm:py-16">
          <motion.div
            animate={{ y: hover ? -5 : 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 18 }}
            className="relative mb-5 flex h-14 w-14 items-center justify-center sm:mb-7 sm:h-16 sm:w-16"
          >
            <motion.span
              className="absolute inset-0 rounded-xl border border-primary/25"
              animate={{
                scale: hover ? [1, 1.22, 1] : 1,
                opacity: hover ? [0.5, 0, 0.5] : 0.3,
              }}
              transition={{ duration: 2, repeat: hover ? Infinity : 0 }}
            />
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <svg
                viewBox="0 0 24 24"
                className="h-6 w-6 text-primary"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 15V4m0 0L8 8m4-4l4 4" />
                <path d="M4 17v2a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-2" />
              </svg>
            </div>
          </motion.div>

          <p className="font-heading text-lg tracking-tight sm:text-xl">
            {dragActive ? "Release to begin" : "Drop your billing and CRM CSVs here"}
          </p>
          <p className="mt-2 max-w-md text-sm text-muted-foreground">
            or{" "}
            <span className="text-foreground/70 underline decoration-primary/50 underline-offset-2">
              click to browse
            </span>{" "}
            Invoice line items and price catalog to start; CRM exports for contract checks
          </p>

          <div className="mt-6 flex flex-col items-center gap-2 text-[0.75rem] text-muted-foreground sm:mt-8 sm:flex-row sm:flex-wrap sm:justify-center sm:gap-x-5 sm:gap-y-2">
            {[
              "Encrypted in transit",
              "Raw CSVs deleted after processing",
              "No account required",
            ].map((t) => (
              <span key={t} className="flex items-center gap-1.5">
                <span className="h-1 w-1 rounded-full bg-primary/50" />
                {t}
              </span>
            ))}
          </div>
        </div>
      </motion.div>

      <div className="flex w-full flex-col items-stretch gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-center">
        <RunFreeAuditCta size="lg" className="w-full justify-center sm:w-auto" />
        <ViewSampleReportCta size="lg" analyticsSource="landing_upload" className="w-full justify-center sm:w-auto" />
      </div>
    </motion.div>
  );
}

function MethodSection() {
  return (
    <section className="mx-auto max-w-marketing px-6 py-16 md:px-10 md:py-28">
      <Reveal>
        <p className="mb-3 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          The method
        </p>
        <h2 className="max-w-2xl font-heading text-[clamp(1.9rem,4vw,3rem)] leading-[1.05] tracking-tight text-balance">
          Three deliberate movements, from raw export to recovered revenue.
        </h2>
      </Reveal>

      <Stagger className="mt-12 grid gap-x-12 gap-y-12 md:mt-20 md:grid-cols-3 md:gap-y-16">
        {METHOD_STEPS.map((s) => (
          <StaggerItem key={s.n}>
            <div>
              <div className="mb-6 flex items-baseline gap-4 border-t border-line pt-5">
                <span className="font-heading text-sm text-primary tnum">{s.n}</span>
                <span className="font-heading text-2xl tracking-tight">{s.title}</span>
              </div>
              <p className="text-pretty leading-relaxed text-muted-foreground">{s.body}</p>
            </div>
          </StaggerItem>
        ))}
      </Stagger>
    </section>
  );
}

export function LandingPageClient() {
  return (
    <>
      <LandingPageTracker />
      <ArrLeakageHero />

      <section className="border-t border-line">
        <div className="mx-auto max-w-marketing px-6 py-14 md:px-10 md:py-28">
          <Reveal className="mx-auto max-w-readable text-center">
            <p className="text-overline text-muted-foreground">Free deterministic audit</p>
            <h2 className="mt-4 font-heading text-[clamp(1.9rem,4vw,3rem)] leading-[1.05] tracking-tight text-balance">
              Ready to find the exact dollars?
            </h2>
            <p className="mt-5 text-pretty text-body leading-relaxed text-muted-foreground md:mt-6">
              Upload billing and CRM CSV exports. Our engine reconciles every row and surfaces missed
              revenue, duplicate charges, and pricing drift in minutes.
            </p>
          </Reveal>

          <div className="mx-auto mt-10 max-w-2xl md:mt-12">
            <HeroUploadZone />
          </div>

          <Reveal delay={0.1} className="mt-10 grid grid-cols-3 gap-3 sm:mt-12 sm:flex sm:flex-wrap sm:justify-center sm:gap-x-10 sm:gap-y-4">
            {[
              [String(VERIFICATION_RULE_COUNT), "verification checks"],
              ["9", "CSV export types"],
              ["< 90 s", "average runtime"],
            ].map(([val, label]) => (
              <div key={label} className="text-center">
                <p className="font-heading text-lg tracking-tight text-foreground tnum sm:text-xl md:text-2xl">
                  {val}
                </p>
                <p className="mt-1 text-[0.7rem] leading-snug text-muted-foreground sm:text-[0.78rem]">
                  {label}
                </p>
              </div>
            ))}
          </Reveal>
        </div>
      </section>

      <section className="border-b border-line">
        <div className="mx-auto grid max-w-marketing grid-cols-1 gap-px bg-line sm:grid-cols-2 md:grid-cols-4">
          {STATS.map((s, i) => (
            <Reveal key={s.label} delay={i * 0.08} className="bg-background px-6 py-8 sm:py-10 md:px-10">
              <div className="font-heading text-3xl tracking-tight tnum md:text-4xl">
                <CountUp
                  to={s.value}
                  prefix={s.prefix}
                  suffix={s.suffix}
                  decimals={s.decimals}
                />
              </div>
              <p className="mt-3 max-w-[16rem] text-[0.82rem] leading-relaxed text-muted-foreground">
                {s.label}
              </p>
            </Reveal>
          ))}
        </div>
      </section>

      <MethodSection />
      <SecuritySummary />
      <FreeReportPreview />
      <SiteFooter />
    </>
  );
}
