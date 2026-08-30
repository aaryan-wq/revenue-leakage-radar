"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight, Copy, Mail } from "lucide-react";

import { CountUp } from "@/components/count-up";
import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { captureEvent } from "@/lib/analytics/client";
import {
  calculateAssessment,
  createShareLink,
  fetchResult,
  saveLead,
} from "@/lib/estimator/api";
import { AnalyticsEvents, formatCurrency, type EstimatorHypothesisBreakdown, type EstimatorResult } from "@rlr/shared";

interface EstimatorResultClientProps {
  assessmentId: string;
}

function toNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeResult(data: EstimatorResult): EstimatorResult {
  const normalizeHypothesis = (item: EstimatorHypothesisBreakdown): EstimatorHypothesisBreakdown => ({
    ...item,
    posterior_probability: toNumber(item.posterior_probability),
    low: toNumber(item.low),
    mid: toNumber(item.mid),
    high: toNumber(item.high),
  });

  return {
    ...data,
    estimate: {
      ...data.estimate,
      low: toNumber(data.estimate.low),
      central: toNumber(data.estimate.central),
      high: toNumber(data.estimate.high),
    },
    monthly: {
      low: toNumber(data.monthly.low),
      central: toNumber(data.monthly.central),
      high: toNumber(data.monthly.high),
    },
    top_hypotheses: data.top_hypotheses.map(normalizeHypothesis),
    hypothesis_breakdown: data.hypothesis_breakdown.map(normalizeHypothesis),
  };
}

export function EstimatorResultClient({ assessmentId }: EstimatorResultClientProps) {
  const router = useRouter();
  const [result, setResult] = useState<EstimatorResult | null>(null);
  const [scenario, setScenario] = useState("central");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shareMessage, setShareMessage] = useState<string | null>(null);
  const [emailSaved, setEmailSaved] = useState(false);

  const loadInitial = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchResult(assessmentId);
      setResult(normalizeResult(data));
      captureEvent(AnalyticsEvents.RESULT_VIEWED, { assessment_id: assessmentId });
    } catch {
      try {
        const calculated = await calculateAssessment(assessmentId, "central");
        setResult(normalizeResult(calculated));
        captureEvent(AnalyticsEvents.RESULT_VIEWED, { assessment_id: assessmentId });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load your estimate");
      }
    } finally {
      setLoading(false);
    }
  }, [assessmentId]);

  useEffect(() => {
    void loadInitial();
  }, [loadInitial]);

  const handleScenario = async (next: string) => {
    setScenario(next);
    setScenarioLoading(true);
    setError(null);
    try {
      captureEvent(AnalyticsEvents.SCENARIO_CHANGED, { assessment_id: assessmentId, scenario: next });
      const calculated = await calculateAssessment(assessmentId, next);
      setResult(normalizeResult(calculated));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update scenario");
    } finally {
      setScenarioLoading(false);
    }
  };

  const handleScanClick = () => {
    if (!result) return;
    captureEvent(AnalyticsEvents.FREE_SCAN_CLICKED, {
      assessment_id: assessmentId,
      estimate_low: result.estimate.low,
      estimate_high: result.estimate.high,
    });
    router.push(`/upload?assessment_id=${assessmentId}`);
  };

  const handleShare = async () => {
    try {
      const share = await createShareLink(assessmentId);
      const url = `${window.location.origin}${share.share_path}`;
      await navigator.clipboard.writeText(url);
      captureEvent(AnalyticsEvents.RESULT_SHARED, { assessment_id: assessmentId });
      setShareMessage("Link copied to clipboard");
    } catch {
      setShareMessage("Unable to create share link. Please try again.");
    }
  };

  const handleEmail = async () => {
    if (!email) return;
    await saveLead(assessmentId, { email });
    captureEvent(AnalyticsEvents.ASSESSMENT_EMAIL_SAVED, { assessment_id: assessmentId });
    setEmailSaved(true);
  };

  if (loading) return <PageLoadingSkeleton message="Preparing your results…" />;

  if (error && !result) {
    return (
      <div className="mx-auto max-w-readable px-6 py-24 text-center md:px-10">
        <HairlineCard padding="lg" className="space-y-6">
          <h1 className="text-h3 text-foreground">We could not load your estimate</h1>
          <p className="text-body text-muted-foreground">{error}</p>
          <Button onClick={() => void loadInitial()} className="min-h-[44px]">
            Try again
          </Button>
        </HairlineCard>
      </div>
    );
  }

  if (!result) return null;

  const paybackPct = result.estimate.low > 0 ? (2500 / result.estimate.low) * 100 : 0;
  const top = result.top_hypotheses[0];
  const maxBreakdown = Math.max(...result.hypothesis_breakdown.slice(0, 5).map((item) => item.high), 1);

  return (
    <div className="mx-auto max-w-marketing space-y-12 px-6 py-12 md:px-10 md:py-16">
      <Reveal>
        <HairlineCard padding="lg" className="overflow-hidden">
          <div className="space-y-8 text-center">
            <p className="text-overline text-muted-foreground">Modeled estimate</p>
            <div className="space-y-4">
              <h1 className="text-h2 text-foreground">Recoverable revenue opportunity</h1>
              <p className="text-metric-xl tabular-nums text-foreground">
                <CountUp to={result.estimate.low} prefix="$" /> to{" "}
                <CountUp to={result.estimate.high} prefix="$" />
              </p>
              <p className="mx-auto max-w-readable text-body text-muted-foreground">
                About {formatCurrency(result.monthly.low)} to {formatCurrency(result.monthly.high)} per month in
                recurring revenue exposure. This is a model, not an audited finding.
              </p>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-2">
              {(["conservative", "central", "aggressive"] as const).map((option) => (
                <Button
                  key={option}
                  variant={scenario === option ? "primary" : "secondary"}
                  onClick={() => void handleScenario(option)}
                  disabled={scenarioLoading}
                  className="min-h-[44px] capitalize"
                >
                  {option}
                </Button>
              ))}
            </div>
          </div>
        </HairlineCard>
      </Reveal>

      {error ? <p className="text-center text-small text-destructive">{error}</p> : null}

      <Stagger className="grid gap-6 md:grid-cols-2">
        <StaggerItem>
          <HairlineCard padding="lg" className="h-full space-y-6">
            <div>
              <p className="text-overline text-muted-foreground">Top drivers</p>
              <h2 className="text-h4 mt-2">Where leakage likely hides</h2>
            </div>
            <div className="space-y-5">
              {result.hypothesis_breakdown.slice(0, 5).map((item) => (
                <div key={item.hypothesis_id} className="space-y-2">
                  <div className="flex items-center justify-between gap-4">
                    <span className="text-body text-foreground">{item.name}</span>
                    <span className="text-small tabular-nums text-muted-foreground">
                      {formatCurrency(item.low)} to {formatCurrency(item.high)}
                    </span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-border/30">
                    <div
                      className="h-full rounded-full bg-primary/80 transition-all"
                      style={{ width: `${Math.max(8, (item.high / maxBreakdown) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </HairlineCard>
        </StaggerItem>

        <StaggerItem>
          <HairlineCard padding="lg" className="h-full space-y-6">
            <div>
              <p className="text-overline text-muted-foreground">Assumptions</p>
              <h2 className="text-h4 mt-2">What would need to be true</h2>
            </div>
            <ul className="space-y-3 text-body text-muted-foreground">
              {result.what_would_need_to_be_true.map((line) => (
                <li key={line} className="flex gap-3">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
                  <span>{line}</span>
                </li>
              ))}
            </ul>
          </HairlineCard>
        </StaggerItem>
      </Stagger>

      {result.narrative ? (
        <Reveal>
          <HairlineCard padding="lg" className="space-y-3">
            <p className="text-overline text-muted-foreground">Summary</p>
            <h2 className="text-h4">{result.narrative.headline}</h2>
            <p className="max-w-readable text-body text-muted-foreground">{result.narrative.summary}</p>
          </HairlineCard>
        </Reveal>
      ) : null}

      <Reveal>
        <HairlineCard padding="lg" className="space-y-6 border-primary/20">
          <div className="space-y-3">
            <p className="text-overline text-muted-foreground">Next step</p>
            <h2 className="text-h3">Replace the model with evidence</h2>
            <p className="max-w-readable text-body text-muted-foreground">
              {top
                ? `Your largest modeled exposure is ${top.name.toLowerCase()}. Upload billing exports to verify with deterministic checks.`
                : "Upload billing exports to verify modeled exposure with deterministic checks."}
            </p>
          </div>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
            <Button onClick={handleScanClick} className="min-h-[44px]">
              Run free billing scan
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <p className="text-caption text-muted-foreground">
              No account required. No payment required.
            </p>
          </div>
          <p className="text-small text-muted-foreground">
            At {formatCurrency(2500)}, the audit pays for itself if it confirms about {paybackPct.toFixed(1)}% of
            the low-end estimate.
          </p>
        </HairlineCard>
      </Reveal>

      <div className="grid gap-6 md:grid-cols-2">
        <HairlineCard padding="md" className="space-y-4">
          <div className="flex items-center gap-2">
            <Mail className="h-4 w-4 text-muted-foreground" />
            <h3 className="text-h4">Email this estimate</h3>
          </div>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            className="w-full rounded-xl border border-border/50 bg-surface-glass-subtle px-4 py-3 text-body min-h-[44px] focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
          <Button variant="secondary" onClick={() => void handleEmail()} disabled={!email || emailSaved} className="min-h-[44px]">
            {emailSaved ? "Sent" : "Send summary"}
          </Button>
        </HairlineCard>

        <HairlineCard padding="md" className="space-y-4">
          <div className="flex items-center gap-2">
            <Copy className="h-4 w-4 text-muted-foreground" />
            <h3 className="text-h4">Share with your team</h3>
          </div>
          <p className="text-small text-muted-foreground">Create a read-only link for finance or RevOps review.</p>
          <Button variant="secondary" onClick={() => void handleShare()} className="min-h-[44px]">
            Copy share link
          </Button>
          {shareMessage ? <p className="text-caption text-muted-foreground">{shareMessage}</p> : null}
        </HairlineCard>
      </div>

      <div className="text-center">
        <Link
          href="/saas-revenue-leakage-calculator/methodology"
          className="text-small text-muted-foreground underline-offset-4 hover:underline"
        >
          Read the methodology
        </Link>
      </div>
    </div>
  );
}
