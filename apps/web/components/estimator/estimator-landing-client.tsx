"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, BarChart3, Clock, Loader2, Shield, ShieldCheck, Sparkles } from "lucide-react";

import { glide, Reveal } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { captureEvent } from "@/lib/analytics/client";
import {
  clearAssessmentSession,
  createAssessment,
  patchAnswers,
  storeAssessmentSession,
} from "@/lib/estimator/api";
import { AnalyticsEvents } from "@rlr/shared";
import { useTrackOnce } from "@/lib/analytics/hooks";
import { cn } from "@/lib/utils";

const TRUST_ITEMS = [
  { icon: Clock, label: "About 5 minutes" },
  { icon: Shield, label: "No billing data" },
  { icon: Sparkles, label: "No account" },
] as const;

const COMPANY_TYPE_OPTIONS = [
  { value: "b2b_saas", label: "B2B SaaS" },
  { value: "b2b_b2c", label: "B2B + B2C" },
  { value: "marketplace", label: "Marketplace" },
] as const;

const HEADLINE_LINES = ["Model your", "leakage exposure"];

const MODEL_STEPS = [
  { icon: Sparkles, label: "Your inputs" },
  { icon: BarChart3, label: "Deterministic model" },
  { icon: ShieldCheck, label: "Modeled range" },
] as const;

function MethodologyTeaser() {
  return (
    <Link
      href="/saas-revenue-leakage-calculator/methodology"
      className="group block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2"
    >
      <HairlineCard
        padding="md"
        interactive
        className="border-line bg-surface-glass-subtle transition-all duration-normal group-hover:border-primary/25 group-hover:shadow-[0_12px_40px_-28px_rgba(15,23,42,0.25)]"
      >
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            <BarChart3 className="h-5 w-5 text-primary" strokeWidth={1.75} aria-hidden />
          </div>
          <div className="min-w-0 flex-1 space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-1">
                <p className="text-h4 text-foreground">How the model works</p>
                <p className="text-small text-muted-foreground">
                  Transparent assumptions, 18 leakage hypotheses, fixed-seed Monte Carlo.
                </p>
              </div>
              <ArrowRight
                className="mt-1 h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-normal group-hover:translate-x-0.5 group-hover:text-foreground"
                aria-hidden
              />
            </div>
            <div className="flex flex-wrap gap-2">
              {MODEL_STEPS.map((step) => (
                <span
                  key={step.label}
                  className="inline-flex items-center gap-1.5 rounded-full border border-line bg-background/70 px-2.5 py-1 text-caption text-muted-foreground"
                >
                  <step.icon className="h-3 w-3 shrink-0" strokeWidth={1.75} aria-hidden />
                  {step.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </HairlineCard>
    </Link>
  );
}

function BusinessTypeOption({
  label,
  isLoading,
  disabled,
  onSelect,
}: {
  label: string;
  isLoading: boolean;
  disabled: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onSelect}
      className={cn(
        "group flex min-h-[44px] w-full items-center justify-between rounded-xl border px-4 py-3 text-left text-small",
        "border-line bg-background/60 text-foreground",
        "transition-all duration-normal motion-reduce:transition-colors",
        "hover:-translate-y-0.5 hover:border-primary/40 hover:bg-secondary/60",
        "hover:shadow-[0_10px_28px_-18px_rgba(15,23,42,0.12)] motion-reduce:hover:translate-y-0 motion-reduce:hover:shadow-none",
        "active:scale-[0.98] motion-reduce:active:scale-100",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2",
        disabled && !isLoading && "opacity-50",
        isLoading && "border-primary/50 bg-secondary shadow-sm",
      )}
    >
      <span className="transition-colors duration-normal group-hover:text-foreground">{label}</span>
      {isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin text-primary" aria-hidden />
      ) : (
        <ArrowRight
          className="h-4 w-4 text-muted-foreground transition-all duration-normal group-hover:translate-x-1 group-hover:text-primary motion-reduce:group-hover:translate-x-0"
          aria-hidden
        />
      )}
    </button>
  );
}

function AssessmentStartPicker() {
  const router = useRouter();
  const [starting, setStarting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelect = async (value: string) => {
    if (starting) return;
    setStarting(value);
    setError(null);
    try {
      clearAssessmentSession();
      const created = await createAssessment();
      storeAssessmentSession(created.assessment_id, created.session_token);
      await patchAnswers(created.assessment_id, [
        { question_id: "profile.company_type", value_enum: value },
      ]);
      captureEvent(AnalyticsEvents.ESTIMATOR_STARTED, {
        source: "landing_first_question",
        company_type: value,
        assessment_id: created.assessment_id,
      });
      captureEvent(AnalyticsEvents.QUESTION_ANSWERED, {
        assessment_id: created.assessment_id,
        question_id: "profile.company_type",
      });
      router.push("/saas-revenue-leakage-calculator/start");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to start assessment");
      setStarting(null);
    }
  };

  return (
    <HairlineCard padding="md" className="relative overflow-hidden border-line bg-surface-glass-subtle">
      <div className="space-y-5">
        <div className="space-y-2">
          <div className="flex items-center justify-between gap-3">
            <p className="text-caption text-muted-foreground">Your company · Question 1</p>
            <p className="text-caption tabular-nums text-muted-foreground">~5 min left</p>
          </div>
          <div className="h-1 overflow-hidden rounded-full bg-border/30">
            <div className="h-full w-[12%] rounded-full bg-primary/70" />
          </div>
        </div>

        <div className="space-y-4">
          <p className="text-h4 text-foreground">What best describes your business?</p>
          <div className="space-y-2">
            {COMPANY_TYPE_OPTIONS.map((option) => (
              <BusinessTypeOption
                key={option.value}
                label={option.label}
                isLoading={starting === option.value}
                disabled={Boolean(starting)}
                onSelect={() => void handleSelect(option.value)}
              />
            ))}
          </div>
        </div>

        {error ? <p className="text-small text-destructive">{error}</p> : null}

        <p className="text-caption text-muted-foreground">Select an option to begin.</p>
      </div>
    </HairlineCard>
  );
}

export function EstimatorLandingClient() {
  useTrackOnce(AnalyticsEvents.ESTIMATOR_VIEWED, { page: "landing" });

  return (
    <>
      <section className="mx-auto flex min-h-[calc(100dvh-72px)] max-w-marketing flex-col justify-center px-6 py-6 md:px-10 md:py-8">
        <div className="grid items-center gap-8 lg:grid-cols-2 lg:gap-12">
          <div className="text-center lg:text-left">
            <motion.p
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: glide }}
              className="text-overline text-muted-foreground"
            >
              Revenue leakage assessment
            </motion.p>
            <h1 className="mt-3 font-heading text-[clamp(1.9rem,3.8vw,2.75rem)] leading-[1.02] tracking-tight text-balance text-foreground">
              {HEADLINE_LINES.map((line, i) => (
                <span key={line} className="block overflow-hidden">
                  <motion.span
                    className="block"
                    initial={{ y: "100%" }}
                    animate={{ y: 0 }}
                    transition={{ duration: 0.85, ease: glide, delay: 0.05 + i * 0.08 }}
                  >
                    {i === 1 ? <span className="italic text-primary">{line}</span> : line}
                  </motion.span>
                </span>
              ))}
            </h1>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, ease: glide, delay: 0.25 }}
              className="mt-4 text-body leading-relaxed text-muted-foreground"
            >
              Structured questions about pricing, contracts, and billing ops. Personalized range and
              drivers at the end.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, ease: glide, delay: 0.35 }}
              className="mt-5 flex flex-wrap justify-center gap-2 lg:justify-start"
            >
              {TRUST_ITEMS.map((item) => (
                <span
                  key={item.label}
                  className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface-glass-subtle px-3 py-1.5 text-caption text-muted-foreground"
                >
                  <item.icon className="h-3 w-3 shrink-0" strokeWidth={1.75} aria-hidden />
                  {item.label}
                </span>
              ))}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, ease: glide, delay: 0.45 }}
              className="mt-8 space-y-4"
            >
              <MethodologyTeaser />
              <p className="text-caption text-muted-foreground lg:max-w-md">
                Directional guidance from your answers, not an audited billing finding.
              </p>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: glide, delay: 0.15 }}
            className="mx-auto w-full max-w-md lg:max-w-none"
          >
            <AssessmentStartPicker />
          </motion.div>
        </div>
      </section>

      <Reveal className="mx-auto max-w-marketing px-6 pb-16 md:px-10">
        <HairlineCard padding="md" subtle className="mx-auto max-w-readable overflow-hidden">
          <div className="flex flex-col items-center gap-4 text-center sm:flex-row sm:justify-between sm:text-left">
            <p className="text-small text-muted-foreground">
              Need evidence from actual billing records? Run the free deterministic scan.
            </p>
            <Link href="/upload" className="shrink-0">
              <Button variant="ghost" className="min-h-[44px]">
                Run free billing scan
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </HairlineCard>
      </Reveal>
    </>
  );
}
