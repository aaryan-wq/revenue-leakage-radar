"use client";

import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { motion } from "framer-motion";

import { CountUp } from "@/components/count-up";
import { glide, Reveal, Stagger, StaggerItem } from "@/components/motion";
import { AnalyticsEvents } from "@rlr/shared";
import { captureEvent } from "@/lib/analytics/client";
import { FreeReportPreview } from "@/components/marketing/free-report-preview";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { LandingPageTracker } from "@/components/analytics/marketing-page-tracker";
import { SiteFooter } from "@/components/site-footer";
import { VERIFICATION_RULE_COUNT } from "@/lib/verification-rules";

const HERO_STATS = [
  [String(VERIFICATION_RULE_COUNT), "verification checks"],
  ["9", "CSV export types"],
  ["< 90 s", "average runtime"],
] as const;

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
    captureEvent(AnalyticsEvents.FREE_AUDIT_CTA_CLICKED, { source: "hero_upload_zone" });
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
      transition={{ duration: 1, ease: glide, delay: 0.4 }}
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

        <div className="relative flex flex-col items-center px-8 py-16 text-center">
          <motion.div
            animate={{ y: hover ? -5 : 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 18 }}
            className="relative mb-7 flex h-16 w-16 items-center justify-center"
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

          <p className="font-heading text-xl tracking-tight">
            {dragActive ? "Release to begin" : "Drop your billing and CRM CSVs here"}
          </p>
          <p className="mt-2 text-sm text-muted-foreground">
            or{" "}
            <span className="text-foreground/70 underline decoration-primary/50 underline-offset-2">
              click to browse
            </span>{" "}
            Invoice line items and price catalog to start; CRM exports for contract checks
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-[0.75rem] text-muted-foreground">
            {["End-to-end encrypted", "No account required", "Results in minutes"].map((t) => (
              <span key={t} className="flex items-center gap-1.5">
                <span className="h-1 w-1 rounded-full bg-primary/50" />
                {t}
              </span>
            ))}
          </div>
        </div>
      </motion.div>

      <RunFreeAuditCta size="lg" />
    </motion.div>
  );
}

function MethodSection() {
  return (
    <section className="mx-auto max-w-marketing px-6 py-28 md:px-10">
      <Reveal>
        <p className="mb-3 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          The method
        </p>
        <h2 className="max-w-2xl font-heading text-[clamp(1.9rem,4vw,3rem)] leading-[1.05] tracking-tight text-balance">
          Three deliberate movements, from raw export to recovered revenue.
        </h2>
      </Reveal>

      <Stagger className="mt-20 grid gap-x-12 gap-y-16 md:grid-cols-3">
        {METHOD_STEPS.map((s) => (
          <StaggerItem key={s.n}>
            <div className="group">
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
      <section className="relative mx-auto max-w-marketing px-6 pt-20 pb-16 md:px-10 md:pt-28 md:pb-24">
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <div>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.9, ease: glide }}
              className="mb-7 inline-flex items-center gap-2.5 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground"
            >
              <span className="h-px w-8 bg-primary/50" />
              Free instant audit
            </motion.p>

            <h1 className="font-heading text-[clamp(2.6rem,5.5vw,4.4rem)] leading-[0.95] tracking-tight text-balance">
              {["Drop billing and CRM CSVs.", "See exactly where", "revenue is leaking."].map((line, i) => (
                <span key={line} className="block overflow-hidden">
                  <motion.span
                    className="block"
                    initial={{ y: "110%" }}
                    animate={{ y: 0 }}
                    transition={{ duration: 1.1, ease: glide, delay: 0.08 + i * 0.12 }}
                  >
                    {i === 1 ? <span className="italic text-primary">{line}</span> : line}
                  </motion.span>
                </span>
              ))}
            </h1>

            <motion.p
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, ease: glide, delay: 0.5 }}
              className="mt-7 text-pretty text-[1.05rem] leading-relaxed text-muted-foreground"
            >
              Upload billing and CRM CSV exports. Our engine reconciles every row and surfaces missed
              revenue, duplicate charges, and pricing drift in minutes. Deterministic checks.
              CFO-grade evidence.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.9, ease: glide, delay: 0.65 }}
              className="mt-10 flex flex-wrap gap-x-8 gap-y-3"
            >
              {HERO_STATS.map(([val, label]) => (
                <div key={label}>
                  <p className="font-heading text-2xl tracking-tight text-foreground tnum">{val}</p>
                  <p className="text-[0.78rem] text-muted-foreground">{label}</p>
                </div>
              ))}
            </motion.div>
          </div>

          <HeroUploadZone />
        </div>
      </section>

      <section className="border-y border-line">
        <div className="mx-auto grid max-w-marketing grid-cols-2 gap-px bg-line md:grid-cols-4">
          {STATS.map((s, i) => (
            <Reveal key={s.label} delay={i * 0.08} className="bg-background px-6 py-10 md:px-10">
              <div className="font-heading text-3xl tracking-tight tnum md:text-4xl">
                <CountUp
                  to={s.value}
                  prefix={s.prefix}
                  suffix={s.suffix}
                  decimals={s.decimals}
                />
              </div>
              <p className="mt-3 text-[0.82rem] leading-relaxed text-muted-foreground">
                {s.label}
              </p>
            </Reveal>
          ))}
        </div>
      </section>

      <MethodSection />
      <FreeReportPreview />
      <SiteFooter />
    </>
  );
}
