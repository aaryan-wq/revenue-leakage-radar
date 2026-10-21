"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ArrowRight, Clock, Loader2, Shield, Sparkles } from "lucide-react";

import { Reveal } from "@/components/motion";
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

function MethodologyTeaser() {
  return (
    <p className="text-small leading-relaxed text-muted-foreground">
      <Link
        href="/saas-revenue-leakage-calculator/methodology"
        className="font-medium text-foreground underline-offset-4 transition-colors hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2"
      >
        How the model works
      </Link>
      : transparent assumptions, 18 leakage hypotheses, fixed-seed Monte Carlo.
    </p>
  );
}

function BusinessTypeOption({
  label,
  isLoading,
  disabled,
  onSelect,
  tile = false,
}: {
  label: string;
  isLoading: boolean;
  disabled: boolean;
  onSelect: () => void;
  tile?: boolean;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onSelect}
      className={cn(
        "group flex w-full rounded-lg border text-left text-sm",
        "border-line bg-background text-foreground",
        "transition-[background-color,border-color,transform] duration-fast ease-glide hover:border-foreground/25 hover:bg-secondary active:scale-[0.98] motion-reduce:transform-none",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        tile
          ? "min-h-24 flex-col items-start justify-between px-5 py-5"
          : "min-h-11 items-center justify-between px-4 py-3",
        disabled && !isLoading && "opacity-50",
        isLoading && "border-foreground bg-secondary",
      )}
    >
      <span className="transition-colors duration-normal group-hover:text-foreground">{label}</span>
      {isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin text-primary" aria-hidden />
      ) : (
        <ArrowRight
          className="h-4 w-4 text-muted-foreground transition-transform duration-fast ease-glide group-hover:translate-x-0.5 motion-reduce:transform-none"
          aria-hidden
        />
      )}
    </button>
  );
}

export function AssessmentStartPicker({
  source = "landing_first_question",
  plain = false,
  layout = "stack",
}: {
  source?: string;
  plain?: boolean;
  layout?: "stack" | "columns";
}) {
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
        source,
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

  const columns = layout === "columns";

  const body = (
    <div className={columns ? "" : "space-y-4"}>
      <div className={columns ? "flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between" : undefined}>
        <p className={columns ? "text-h3 text-foreground" : "text-h4 text-foreground"}>
          What best describes your business?
        </p>
        {plain ? (
          <p className="text-small text-muted-foreground">
            About 5 minutes. No billing data. No account.
          </p>
        ) : null}
      </div>
      <div className={columns ? "mt-6 grid gap-3 sm:grid-cols-3" : "space-y-2"}>
        {COMPANY_TYPE_OPTIONS.map((option) => (
          <BusinessTypeOption
            key={option.value}
            label={option.label}
            isLoading={starting === option.value}
            disabled={Boolean(starting)}
            tile={columns}
            onSelect={() => void handleSelect(option.value)}
          />
        ))}
      </div>
      {error ? <p className="text-small mt-3 text-destructive">{error}</p> : null}
      {plain ? null : <p className="text-caption text-muted-foreground">Select an option to begin.</p>}
    </div>
  );

  if (plain) return body;

  return (
    <HairlineCard padding="md" className="relative overflow-hidden border-line">
      {body}
    </HairlineCard>
  );
}

export function EstimatorLandingClient() {
  useTrackOnce(AnalyticsEvents.ESTIMATOR_VIEWED, { page: "landing" });

  return (
    <>
      <section className="bg-field">
      <div className="mx-auto flex min-h-[calc(100dvh-4rem)] max-w-marketing flex-col justify-center px-6 py-10 md:px-10 md:py-16">
        <div className="grid items-center gap-8 lg:grid-cols-2 lg:gap-12">
          <div className="text-center lg:text-left">
            <h1 className="text-h1 text-balance text-foreground">Model your leakage exposure.</h1>
            <p className="text-body mt-4 text-muted-foreground">
              Structured questions about pricing, contracts, and billing ops. Personalized range and
              drivers at the end.
            </p>

            <div className="mt-5 flex flex-wrap justify-center gap-x-4 gap-y-2 lg:justify-start">
              {TRUST_ITEMS.map((item) => (
                <span
                  key={item.label}
                  className="inline-flex items-center gap-1.5 text-sm text-muted-foreground"
                >
                  <item.icon className="h-3.5 w-3.5 shrink-0 text-primary" strokeWidth={1.75} aria-hidden />
                  {item.label}
                </span>
              ))}
            </div>

            <div className="mt-8 space-y-4">
              <MethodologyTeaser />
              <p className="text-caption text-muted-foreground lg:max-w-md">
                Directional guidance from your answers, not an audited billing finding.
              </p>
            </div>
          </div>

          <div className="mx-auto w-full max-w-md lg:max-w-none">
            <AssessmentStartPicker />
          </div>
        </div>
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
