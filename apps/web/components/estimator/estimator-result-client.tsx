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
import {
  AnalyticsEvents,
  formatCurrency,
  type EstimatorHypothesisBreakdown,
  type EstimatorMechanismInsight,
  type EstimatorResult,
} from "@rlr/shared";

interface EstimatorResultClientProps {
  assessmentId: string;
}

const SCENARIOS = [
  {
    id: "conservative",
    label: "Conservative",
    subtitle: "P10 to P50 band",
  },
  {
    id: "central",
    label: "Expected",
    subtitle: "P25 to P75 band",
  },
  {
    id: "aggressive",
    label: "Upside",
    subtitle: "P50 to P90 band",
  },
] as const;

function toNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeHypothesis(item: EstimatorHypothesisBreakdown): EstimatorHypothesisBreakdown {
  const expected = toNumber(item.expected ?? item.mid);
  return {
    ...item,
    posterior_probability: toNumber(item.posterior_probability),
    expected,
    low: toNumber(item.low),
    mid: toNumber(item.mid ?? expected),
    high: toNumber(item.high),
    pct_of_arr: toNumber(item.pct_of_arr),
    likelihood: toNumber(item.likelihood),
    share_of_total: toNumber(item.share_of_total),
  };
}

function normalizeResult(data: EstimatorResult): EstimatorResult {
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
    detectable: {
      low: toNumber(data.detectable?.low),
      high: toNumber(data.detectable?.high),
    },
    top_hypotheses: (data.top_hypotheses ?? []).map(normalizeHypothesis),
    hypothesis_breakdown: (data.hypothesis_breakdown ?? []).map(normalizeHypothesis),
    mechanism_insights: data.mechanism_insights ?? [],
    verification_preview: data.verification_preview ?? [],
    calculation_summary: data.calculation_summary,
  };
}

function insightForHypothesis(
  insights: EstimatorMechanismInsight[],
  hypothesisId: string
): string | undefined {
  return insights.find((item) => item.hypothesis_id === hypothesisId)?.insight;
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
      let data: EstimatorResult;
      try {
        data = await fetchResult(assessmentId);
      } catch {
        data = await calculateAssessment(assessmentId, "central");
      }
      setScenario(data.scenario ?? "central");
      setResult(normalizeResult(data));
      captureEvent(AnalyticsEvents.RESULT_VIEWED, { assessment_id: assessmentId });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load your estimate");
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

  const profile = result.profile_summary;
  const mechanisms = result.top_hypotheses.slice(0, 5);
  const maxExpected = Math.max(...mechanisms.map((item) => item.expected), 1);
  const paybackPct = result.estimate.low > 0 ? (2500 / result.estimate.low) * 100 : 0;
  const top = result.top_hypotheses[0];
  const activeScenario = SCENARIOS.find((item) => item.id === scenario);
  const calc = result.calculation_summary;
  const pctOfArr = calc?.pct_of_arr ?? (result.arr_usd ? (result.estimate.central / result.arr_usd) * 100 : 0);
  const medianRun = result.estimate.median_run ?? calc?.median_run;
  const showMedianNote =
    medianRun !== undefined && medianRun !== result.estimate.central && result.estimate.central > 0;

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
              <p className="text-body tabular-nums text-foreground">
                Expected: {formatCurrency(result.estimate.central)} ARR ({pctOfArr.toFixed(2)}% of ARR)
              </p>
              {showMedianNote ? (
                <p className="text-small tabular-nums text-muted-foreground">
                  Median simulation run: {formatCurrency(medianRun)}. Expected uses the average across all 10,000
                  runs.
                </p>
              ) : null}
              <p className="mx-auto max-w-readable text-body text-muted-foreground">
                About {formatCurrency(result.monthly.central)}/mo expected ({formatCurrency(result.monthly.low)} to{" "}
                {formatCurrency(result.monthly.high)} band).
              </p>
              {activeScenario ? (
                <p className="text-caption text-muted-foreground">
                  {activeScenario.label} band: {calc?.scenario_band_label ?? activeScenario.subtitle}. Modeled
                  estimate, not an audited finding.
                </p>
              ) : null}
            </div>

            <div className="space-y-3">
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
              <p className="text-center text-caption text-muted-foreground">
                Scenarios change the percentile band, not your answers.
              </p>
            </div>
          </div>
        </HairlineCard>
      </Reveal>

      {error ? <p className="text-center text-small text-destructive">{error}</p> : null}

      {calc && calc.explanation_bullets.length > 0 ? (
        <Reveal>
          <HairlineCard padding="lg" className="space-y-4">
            <div>
              <p className="text-overline text-muted-foreground">Model calculation</p>
              <h2 className="text-h4 mt-2">How this number was derived</h2>
            </div>
            <ul className="space-y-3">
              {calc.explanation_bullets.map((bullet) => (
                <li key={bullet} className="flex gap-3 text-small text-muted-foreground">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
                  <span>{bullet}</span>
                </li>
              ))}
            </ul>
          </HairlineCard>
        </Reveal>
      ) : null}

      {profile ? (
        <Reveal>
          <HairlineCard padding="lg" className="space-y-6">
            <div>
              <p className="text-overline text-muted-foreground">Your profile</p>
              <h2 className="text-h4 mt-2">What you told us</h2>
            </div>
            <dl className="grid gap-4 sm:grid-cols-3">
              <div>
                <dt className="text-caption text-muted-foreground">ARR</dt>
                <dd className="text-body tabular-nums text-foreground">{formatCurrency(profile.arr_usd)}</dd>
              </div>
              {profile.customer_count ? (
                <div>
                  <dt className="text-caption text-muted-foreground">Customers</dt>
                  <dd className="text-body tabular-nums text-foreground">
                    {profile.customer_count.toLocaleString()}
                  </dd>
                </div>
              ) : null}
              <div>
                <dt className="text-caption text-muted-foreground">Complexity</dt>
                <dd className="text-body text-foreground">{profile.complexity_label}</dd>
              </div>
            </dl>
            {profile.risk_flags.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {profile.risk_flags.map((flag) => (
                  <Badge key={flag} variant="warning">
                    {flag}
                  </Badge>
                ))}
              </div>
            ) : null}
          </HairlineCard>
        </Reveal>
      ) : null}

      {mechanisms.length > 0 ? (
        <Stagger className="space-y-6">
          <div>
            <p className="text-overline text-muted-foreground">Top mechanisms</p>
            <h2 className="text-h4 mt-2">Mechanism math</h2>
          </div>
          {mechanisms.map((item) => {
            const insight = insightForHypothesis(result.mechanism_insights ?? [], item.hypothesis_id);
            return (
              <StaggerItem key={item.hypothesis_id}>
                <HairlineCard padding="lg" className="space-y-4">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <h3 className="text-body font-medium text-foreground">{item.name}</h3>
                    <p className="shrink-0 text-body tabular-nums text-foreground">
                      {formatCurrency(item.expected)}
                    </p>
                  </div>
                  {insight ? (
                    <p className="max-w-readable text-small text-muted-foreground">{insight}</p>
                  ) : null}
                  <div className="h-1.5 overflow-hidden rounded-full bg-border/30">
                    <div
                      className="h-full rounded-full bg-primary/80 transition-all duration-300"
                      style={{ width: `${Math.max(8, (item.expected / maxExpected) * 100)}%` }}
                    />
                  </div>
                </HairlineCard>
              </StaggerItem>
            );
          })}
        </Stagger>
      ) : null}

      {result.verification_preview && result.verification_preview.length > 0 ? (
        <Reveal>
          <HairlineCard padding="lg" className="space-y-6">
            <div>
              <p className="text-overline text-muted-foreground">Verification</p>
              <h2 className="text-h4 mt-2">Scan rules for top mechanisms</h2>
            </div>
            <div className="space-y-5">
              {result.verification_preview.map((entry) => (
                <div key={entry.hypothesis_id} className="space-y-2">
                  <p className="text-body font-medium text-foreground">{entry.hypothesis_name}</p>
                  <ul className="flex flex-wrap gap-2">
                    {entry.rules.map((rule) => (
                      <Badge key={rule.rule_id} variant="gray">
                        {rule.name}
                      </Badge>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </HairlineCard>
        </Reveal>
      ) : null}

      {result.detectable.high > 0 ? (
        <Reveal>
          <HairlineCard padding="lg" className="space-y-3">
            <p className="text-overline text-muted-foreground">Detectable range</p>
            <h2 className="text-h4">Likely identifiable from billing exports</h2>
            <p className="text-body tabular-nums text-foreground">
              {formatCurrency(result.detectable.low)} to {formatCurrency(result.detectable.high)} ARR
            </p>
            <p className="max-w-readable text-small text-muted-foreground">
              Portion of the modeled range matchable from subscription and invoice exports.
            </p>
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
