"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight, Mail, RotateCcw, Share2 } from "lucide-react";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { captureEvent } from "@/lib/analytics/client";
import { toast } from "@/lib/toast";
import { buildEstimatorCtaPaybackLine } from "@/lib/audit-roi-content";
import { EstimatorShareModal } from "@/components/estimator/estimator-share-modal";
import {
  calculateAssessment,
  clearAssessmentSession,
  fetchAssessment,
  fetchResult,
  saveLead,
  storeAssessmentId,
} from "@/lib/estimator/api";
import { AssessmentResumeBanner } from "@/components/estimator/assessment-resume-prompt";
import { EstimatorRoiBanner } from "@/components/estimator/estimator-roi-banner";
import {
  EstimatorIncompleteEstimateNotice,
  EstimatorResultHero,
  EstimatorSensitivityUpsell,
} from "@/components/estimator/estimator-result-hero";
import {
  AnalyticsEvents,
  computeAuditRoi,
  formatCurrency,
  VERIFICATION_REPORT_BASE_FEE_USD,
  type EstimatorHypothesisBreakdown,
  type EstimatorMechanismInsight,
  type EstimatorResult,
  type EstimatorResumeState,
  type EstimatorRuleBreakdown,
} from "@rlr/shared";

interface EstimatorResultClientProps {
  assessmentId: string;
}

const DISPLAY_SCENARIO = "aggressive";

function toNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeRule(row: EstimatorRuleBreakdown): EstimatorRuleBreakdown {
  return {
    ...row,
    expected: toNumber(row.expected),
    low: toNumber(row.low),
    high: toNumber(row.high),
    p90: toNumber(row.p90),
    posterior_probability: toNumber(row.posterior_probability),
    detectability: toNumber(row.detectability),
    pct_of_arr: toNumber(row.pct_of_arr),
    likelihood: toNumber(row.likelihood),
    share_of_total: toNumber(row.share_of_total),
  };
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
      stress_p90: toNumber(data.estimate.stress_p90),
      theoretical_stack_p90: toNumber(data.estimate.theoretical_stack_p90),
      recoverable: toNumber(data.estimate.recoverable),
      at_risk: toNumber(data.estimate.at_risk),
      overlap_discount: toNumber(data.estimate.overlap_discount),
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
    rule_breakdown: (data.rule_breakdown ?? []).map(normalizeRule),
    display_rollups: data.display_rollups ?? [],
    coverage_bridge: data.coverage_bridge,
    mechanism_insights: data.mechanism_insights ?? [],
    rule_insights: data.rule_insights ?? [],
    verification_preview: data.verification_preview ?? [],
    calculation_summary: data.calculation_summary,
    benchmark_context: data.benchmark_context ?? null,
  };
}

function mechanismAmount(item: EstimatorHypothesisBreakdown): number {
  return Math.max(item.expected, item.high, item.mid ?? 0);
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
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [shareOpen, setShareOpen] = useState(false);
  const [emailSaved, setEmailSaved] = useState(false);
  const [emailSending, setEmailSending] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [resume, setResume] = useState<EstimatorResumeState | null>(null);

  const loadInitial = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [assessmentState, resultResponse] = await Promise.allSettled([
        fetchAssessment(assessmentId),
        fetchResult(assessmentId),
      ]);

      if (assessmentState.status === "fulfilled") {
        setResume(assessmentState.value.resume ?? null);
        storeAssessmentId(assessmentId);
      }

      let data: EstimatorResult;
      if (resultResponse.status === "fulfilled" && resultResponse.value.scenario === DISPLAY_SCENARIO) {
        data = resultResponse.value;
      } else {
        data = await calculateAssessment(assessmentId, DISPLAY_SCENARIO);
      }
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

  const handleScanClick = () => {
    if (!result) return;
    captureEvent(AnalyticsEvents.FREE_SCAN_CLICKED, {
      assessment_id: assessmentId,
      estimate_low: result.estimate.low,
      estimate_high: result.estimate.high,
    });
    router.push(`/upload?assessment_id=${assessmentId}`);
  };

  const handleEmail = async () => {
    const trimmed = email.trim();
    if (!trimmed) return;
    setEmailSending(true);
    setEmailError(null);
    try {
      const response = await saveLead(assessmentId, { email: trimmed });
      captureEvent(AnalyticsEvents.ASSESSMENT_EMAIL_SAVED, { assessment_id: assessmentId });
      if (response.email_sent) {
        setEmailSaved(true);
        toast.success("Estimate sent. Check your inbox.");
      } else {
        setEmailSaved(true);
        toast.info("We saved your email, but could not deliver the summary right now. Try again shortly.");
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to send your estimate";
      setEmailError(message);
      toast.error(message);
    } finally {
      setEmailSending(false);
    }
  };

  const handleAnswerNewQuestions = () => {
    storeAssessmentId(assessmentId);
    router.push(`/saas-revenue-leakage-calculator/start?assessment_id=${assessmentId}`);
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
  const maxMechanism = Math.max(...mechanisms.map(mechanismAmount), 1);
  const ctaHigh = result.estimate.high;
  const roiMetrics = computeAuditRoi(ctaHigh);
  const ctaPaybackLine = roiMetrics ? buildEstimatorCtaPaybackLine(roiMetrics) : null;
  const top = result.top_hypotheses[0];

  return (
    <div className="mx-auto max-w-marketing space-y-10 px-6 py-12 md:px-10 md:py-16">
      {resume ? (
        <AssessmentResumeBanner resume={resume} onAnswer={handleAnswerNewQuestions} />
      ) : null}
      {resume?.has_pending_questions && !resume.requires_reanswer ? (
        <EstimatorIncompleteEstimateNotice
          pendingCount={resume.pending_count}
          onAnswer={handleAnswerNewQuestions}
        />
      ) : null}
      <Reveal>
        <EstimatorResultHero result={result} />
      </Reveal>

      <EstimatorRoiBanner estimateHighUsd={ctaHigh} />

      <EstimatorSensitivityUpsell drivers={result.drivers} />

      {error ? <p className="text-center text-small text-destructive">{error}</p> : null}

      {profile ? (
        <Reveal>
          <HairlineCard padding="lg" className="space-y-4">
            <h2 className="text-h4 text-foreground">Your profile</h2>
            <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <dt className="text-caption text-muted-foreground">Estimated recoverable</dt>
                <dd className="text-metric-xl tabular-nums text-foreground">
                  ~{formatCurrency(result.estimate.high)}
                </dd>
              </div>
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
                <dt className="text-caption text-muted-foreground">Billing complexity</dt>
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
            <h2 className="text-h4 text-foreground">Where it likely comes from</h2>
            <p className="text-small mt-2 text-muted-foreground">
              These categories overlap and are not additive.
            </p>
          </div>
          {mechanisms.map((item) => {
            const amount = mechanismAmount(item);
            const insight = insightForHypothesis(result.mechanism_insights ?? [], item.hypothesis_id);
            return (
              <StaggerItem key={item.hypothesis_id}>
                <HairlineCard padding="lg" className="space-y-4">
                  <div className="space-y-2">
                    <h3 className="text-body font-medium text-foreground">{item.name}</h3>
                    <p className="text-metric-xl tabular-nums text-foreground">
                      ~{formatCurrency(amount)}
                      <span className="text-h4 text-muted-foreground"> /year</span>
                    </p>
                  </div>
                  {insight ? (
                    <p className="max-w-readable text-small text-muted-foreground">{insight}</p>
                  ) : null}
                  <div className="h-2 overflow-hidden rounded-full bg-border/30">
                    <div
                      className="h-full rounded-full bg-primary/80 transition-all duration-300"
                      style={{ width: `${Math.max(8, (amount / maxMechanism) * 100)}%` }}
                    />
                  </div>
                </HairlineCard>
              </StaggerItem>
            );
          })}
        </Stagger>
      ) : null}

      <Reveal>
        <HairlineCard padding="lg" className="space-y-6 border-primary/20">
          <div className="space-y-3">
            <h2 className="text-h3 text-foreground">Confirm with a free billing scan</h2>
            <p className="max-w-readable text-body text-muted-foreground">
              {top
                ? `Your largest likely source is ${top.name.toLowerCase()}. Upload billing exports to replace this estimate with evidence-backed findings.`
                : "Upload billing exports to replace this estimate with evidence-backed findings."}
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <Button onClick={handleScanClick} className="min-h-[44px]">
              {ctaHigh >= 100_000
                ? `Confirm ~${formatCurrency(ctaHigh)}+ with a free billing scan`
                : "Run free billing scan"}
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
          <p className="text-small font-medium text-foreground">
            {ctaPaybackLine ?? `A ${formatCurrency(VERIFICATION_REPORT_BASE_FEE_USD)} audit pays for itself when billing data confirms enough of this estimate.`}
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
              onChange={(e) => {
                setEmail(e.target.value);
                if (emailError) setEmailError(null);
                if (emailSaved) setEmailSaved(false);
              }}
              placeholder="you@company.com"
              className="w-full rounded-xl border border-border/50 bg-surface-glass-subtle px-4 py-3 text-body min-h-[44px] focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
            {emailError ? <p className="text-small text-destructive">{emailError}</p> : null}
            <Button
              variant="secondary"
              onClick={() => void handleEmail()}
              disabled={!email.trim() || emailSending || emailSaved}
              className="min-h-[44px]"
            >
              {emailSending ? "Sending..." : emailSaved ? "Sent" : "Send summary"}
            </Button>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Share2 className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-h4">Share with your team</h3>
            </div>
            <p className="text-small text-muted-foreground">
              Send a read-only link to finance or RevOps, or share on LinkedIn and email.
            </p>
            <Button
              variant="secondary"
              onClick={() => setShareOpen(true)}
              className="min-h-[44px]"
            >
              <Share2 className="mr-2 h-4 w-4" />
              Share estimate
            </Button>
          </div>
        </div>
      </HairlineCard>

      <EstimatorShareModal
        open={shareOpen}
        onClose={() => setShareOpen(false)}
        assessmentId={assessmentId}
        estimateHigh={result.estimate.high}
      />
    </div>
  );
}
