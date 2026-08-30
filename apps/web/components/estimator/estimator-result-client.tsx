"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight, Copy, Mail, RotateCcw } from "lucide-react";

import { CountUp } from "@/components/count-up";
import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { captureEvent } from "@/lib/analytics/client";
import {
  calculateAssessment,
  clearAssessmentSession,
  createShareLink,
  fetchResult,
  saveLead,
} from "@/lib/estimator/api";
import { AnalyticsEvents, formatCurrency, type EstimatorHypothesisBreakdown, type EstimatorResult } from "@rlr/shared";

interface EstimatorResultClientProps {
  assessmentId: string;
}

const SCENARIOS = [
  { id: "conservative", label: "Conservative" },
  { id: "central", label: "Expected" },
  { id: "aggressive", label: "Upside" },
] as const;

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
    top_hypotheses: (data.top_hypotheses ?? []).map(normalizeHypothesis),
    hypothesis_breakdown: (data.hypothesis_breakdown ?? []).map(normalizeHypothesis),
    what_would_need_to_be_true: data.what_would_need_to_be_true ?? [],
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

  const handleRedo = () => {
    clearAssessmentSession();
    router.push("/saas-revenue-leakage-calculator/start");
  };

  if (loading) return <PageLoadingSkeleton message="Preparing your results…" />;

  if (error && !result) {
    return (
      <div className="mx-auto max-w-readable px-6 py-24 text-center md:px-10">
        <HairlineCard padding="lg" className="space-y-6">
          <h1 className="text-h3 text-foreground">We could not load your estimate</h1>
          <p className="text-body text-muted-foreground">{error}</p>
          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button onClick={() => void loadInitial()} className="min-h-[44px]">
              Try again
            </Button>
            <Button variant="secondary" onClick={handleRedo} className="min-h-[44px]">
              Start over
            </Button>
          </div>
        </HairlineCard>
      </div>
    );
  }

  if (!result) return null;

  const paybackPct = result.estimate.low > 0 ? (2500 / result.estimate.low) * 100 : 0;
  const top = result.top_hypotheses[0];
  const drivers = result.hypothesis_breakdown.slice(0, 5);
  const maxBreakdown = Math.max(...drivers.map((item) => item.high), 1);
  const assumptions = result.what_would_need_to_be_true;

  return (
    <div className="mx-auto max-w-marketing space-y-10 px-6 py-12 md:px-10 md:py-16">
      <Reveal>
        <HairlineCard padding="lg" className="overflow-hidden">
          <div className="space-y-8">
            <div className="flex flex-wrap items-center justify-center gap-2">
              <Badge variant="info">Modeled estimate</Badge>
              {result.complexity?.label ? (
                <Badge variant="gray">{result.complexity.label} complexity</Badge>
              ) : null}
              {result.confidence ? <Badge variant="success">{result.confidence} confidence</Badge> : null}
            </div>

            <div className="space-y-4 text-center">
              <h1 className="text-h2 text-foreground">Recoverable revenue opportunity</h1>
              <p className="text-metric-xl tabular-nums text-foreground">
                <CountUp to={result.estimate.low} prefix="$" /> to{" "}
                <CountUp to={result.estimate.high} prefix="$" />
              </p>
              <p className="mx-auto max-w-readable text-body text-muted-foreground">
                About {formatCurrency(result.monthly.low)} to {formatCurrency(result.monthly.high)} per month.
                Expected midpoint: {formatCurrency(result.estimate.central)} ARR.
              </p>
              <p className="text-caption text-muted-foreground">
                Directional model only. Not an audited billing finding.
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-2">
              {SCENARIOS.map((option) => (
                <Button
                  key={option.id}
                  variant={scenario === option.id ? "primary" : "secondary"}
                  onClick={() => void handleScenario(option.id)}
                  disabled={scenarioLoading}
                  className="min-h-[44px]"
                >
                  {option.label}
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
              <p className="text-overline text-muted-foreground">Exposure drivers</p>
              <h2 className="text-h4 mt-2">Where leakage likely hides</h2>
            </div>
            {drivers.length > 0 ? (
              <div className="space-y-5">
                {drivers.map((item) => (
                  <div key={item.hypothesis_id} className="space-y-2">
                    <div className="flex items-start justify-between gap-4">
                      <span className="text-body text-foreground">{item.name}</span>
                      <span className="shrink-0 text-small tabular-nums text-muted-foreground">
                        {formatCurrency(item.low)} to {formatCurrency(item.high)}
                      </span>
                    </div>
                    <div className="h-1.5 overflow-hidden rounded-full bg-border/30">
                      <div
                        className="h-full rounded-full bg-primary/80 transition-all duration-300"
                        style={{ width: `${Math.max(8, (item.high / maxBreakdown) * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-body text-muted-foreground">No driver breakdown available for this scenario.</p>
            )}
            <p className="text-caption text-muted-foreground">
              Ranges overlap and are correlation-adjusted. Do not sum them independently.
            </p>
          </HairlineCard>
        </StaggerItem>

        <StaggerItem>
          <HairlineCard padding="lg" className="h-full space-y-6">
            <div>
              <p className="text-overline text-muted-foreground">Assumptions</p>
              <h2 className="text-h4 mt-2">What would need to be true</h2>
            </div>
            {assumptions.length > 0 ? (
              <ul className="space-y-3 text-body text-muted-foreground">
                {assumptions.map((line) => (
                  <li key={line} className="flex gap-3">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
                    <span>{line}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-body text-muted-foreground">
                No assumption summary was generated for this run.
              </p>
            )}
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
            <h2 className="text-h3">Verify with billing records</h2>
            <p className="max-w-readable text-body text-muted-foreground">
              {top
                ? `Your largest modeled exposure is ${top.name.toLowerCase()}. Upload exports to replace the estimate with evidence-backed findings.`
                : "Upload billing exports to replace the estimate with evidence-backed findings."}
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <Button onClick={handleScanClick} className="min-h-[44px]">
              Run free billing scan
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button variant="secondary" onClick={handleRedo} className="min-h-[44px]">
              <RotateCcw className="mr-2 h-4 w-4" />
              Retake assessment
            </Button>
            <Link href="/saas-revenue-leakage-calculator/methodology">
              <Button variant="ghost" className="min-h-[44px]">
                View methodology
              </Button>
            </Link>
          </div>
          <p className="text-small text-muted-foreground">
            A {formatCurrency(2500)} audit pays for itself if it confirms about {paybackPct.toFixed(1)}% of the
            low-end estimate.
          </p>
        </HairlineCard>
      </Reveal>

      <HairlineCard padding="lg" className="space-y-6">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
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
            <Button
              variant="secondary"
              onClick={() => void handleEmail()}
              disabled={!email || emailSaved}
              className="min-h-[44px]"
            >
              {emailSaved ? "Sent" : "Send summary"}
            </Button>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Copy className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-h4">Share with your team</h3>
            </div>
            <p className="text-small text-muted-foreground">
              Create a read-only link for finance or RevOps review.
            </p>
            <Button variant="secondary" onClick={() => void handleShare()} className="min-h-[44px]">
              Copy share link
            </Button>
            {shareMessage ? <p className="text-caption text-muted-foreground">{shareMessage}</p> : null}
          </div>
        </div>
      </HairlineCard>
    </div>
  );
}
