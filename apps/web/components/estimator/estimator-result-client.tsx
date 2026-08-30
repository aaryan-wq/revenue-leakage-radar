"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";

import { CountUp } from "@/components/count-up";
import { Reveal } from "@/components/motion";
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
import { AnalyticsEvents, formatCurrency, type EstimatorResult } from "@rlr/shared";

interface EstimatorResultClientProps {
  assessmentId: string;
}

export function EstimatorResultClient({ assessmentId }: EstimatorResultClientProps) {
  const router = useRouter();
  const [result, setResult] = useState<EstimatorResult | null>(null);
  const [scenario, setScenario] = useState("central");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [shareMessage, setShareMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchResult(assessmentId);
      setResult(data);
      captureEvent(AnalyticsEvents.RESULT_VIEWED, { assessment_id: assessmentId });
    } catch {
      const calculated = await calculateAssessment(assessmentId, scenario);
      setResult(calculated);
    } finally {
      setLoading(false);
    }
  }, [assessmentId, scenario]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleScenario = async (next: string) => {
    setScenario(next);
    captureEvent(AnalyticsEvents.SCENARIO_CHANGED, { assessment_id: assessmentId, scenario: next });
    const calculated = await calculateAssessment(assessmentId, next);
    setResult(calculated);
  };

  const handleScanClick = () => {
    captureEvent(AnalyticsEvents.FREE_SCAN_CLICKED, {
      assessment_id: assessmentId,
      estimate_low: result?.estimate.low,
      estimate_high: result?.estimate.high,
    });
    router.push(`/upload?assessment_id=${assessmentId}`);
  };

  const handleShare = async () => {
    const share = await createShareLink(assessmentId);
    captureEvent(AnalyticsEvents.RESULT_SHARED, { assessment_id: assessmentId });
    setShareMessage(`Share link copied path: ${share.share_path}`);
  };

  const handleEmail = async () => {
    if (!email) return;
    await saveLead(assessmentId, { email });
    captureEvent(AnalyticsEvents.ASSESSMENT_EMAIL_SAVED, { assessment_id: assessmentId });
  };

  if (loading || !result) return <PageLoadingSkeleton message="Loading your estimate…" />;

  const paybackPct = result.estimate.low > 0 ? (2500 / result.estimate.low) * 100 : 0;
  const top = result.top_hypotheses[0];

  return (
    <div className="mx-auto max-w-report space-y-10 px-6 py-12 md:px-10">
      <Reveal>
        <HairlineCard padding="lg" className="space-y-6">
          <p className="text-overline text-muted-foreground">Modeled estimate, not a billing finding</p>
          <h1 className="text-h2">Your modeled revenue leakage opportunity</h1>
          <p className="text-metric-xl tabular-nums text-foreground">
            <CountUp to={result.estimate.low} prefix="$" /> to{" "}
            <CountUp to={result.estimate.high} prefix="$" /> ARR
          </p>
          <p className="text-body text-muted-foreground">
            Equivalent to approximately {formatCurrency(result.monthly.low)} to{" "}
            {formatCurrency(result.monthly.high)} per month of recurring revenue exposure.
          </p>
          <p className="text-small text-muted-foreground">
            Estimate confidence: {result.confidence}. Model maturity: Structural (Stage 0).
          </p>
        </HairlineCard>
      </Reveal>

      <HairlineCard padding="lg" className="space-y-4">
        <h2 className="text-h4">Scenario</h2>
        <div className="flex flex-wrap gap-2">
          {(["conservative", "central", "aggressive"] as const).map((option) => (
            <Button
              key={option}
              variant={scenario === option ? "primary" : "secondary"}
              onClick={() => void handleScenario(option)}
              className="min-h-[44px] capitalize"
            >
              {option}
            </Button>
          ))}
        </div>
      </HairlineCard>

      <HairlineCard padding="lg" className="space-y-4">
        <h2 className="text-h4">Exposure breakdown</h2>
        <div className="space-y-3">
          {result.hypothesis_breakdown.slice(0, 5).map((item) => (
            <div key={item.hypothesis_id} className="flex items-center justify-between gap-4">
              <span className="text-body">{item.name}</span>
              <span className="text-small tabular-nums text-muted-foreground">
                {formatCurrency(item.low)} to {formatCurrency(item.high)}
              </span>
            </div>
          ))}
        </div>
        <p className="text-caption text-muted-foreground">
          Ranges overlap and are adjusted for correlation. Do not add them independently.
        </p>
      </HairlineCard>

      <HairlineCard padding="lg" className="space-y-4">
        <h2 className="text-h4">What would need to be true?</h2>
        <ul className="list-disc space-y-2 pl-5 text-body text-muted-foreground">
          {result.what_would_need_to_be_true.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </HairlineCard>

      {result.narrative ? (
        <HairlineCard padding="lg" className="space-y-3">
          <h2 className="text-h4">{result.narrative.headline}</h2>
          <p className="text-body text-muted-foreground">{result.narrative.summary}</p>
        </HairlineCard>
      ) : null}

      <HairlineCard padding="lg" className="space-y-4">
        <h2 className="text-h4">Audit payback</h2>
        <p className="text-body text-muted-foreground">
          The audit only needs to identify about {paybackPct.toFixed(1)}% of the low-end modeled
          opportunity to pay for itself at {formatCurrency(2500)}.
        </p>
      </HairlineCard>

      <HairlineCard padding="lg" className="space-y-6 border-primary/20">
        <h2 className="text-h3">Replace the estimate with evidence</h2>
        <p className="text-body text-muted-foreground">
          {top
            ? `Your largest modeled exposure is ${top.name.toLowerCase()}. Run a billing scan to verify with actual records.`
            : "Run a billing scan to verify modeled exposure with actual records."}
        </p>
        <Button onClick={handleScanClick} className="min-h-[44px]">
          Run Free Deterministic Scan
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
        <p className="text-caption text-muted-foreground">
          No sales call required. No payment required. Upload billing exports only.
        </p>
      </HairlineCard>

      <div className="grid gap-6 md:grid-cols-2">
        <HairlineCard padding="md" className="space-y-3">
          <h3 className="text-h4">Email me this assessment</h3>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            className="w-full rounded-xl border border-border/60 bg-surface-glass-subtle px-4 py-3 min-h-[44px]"
          />
          <Button variant="secondary" onClick={() => void handleEmail()} className="min-h-[44px]">
            Send summary
          </Button>
        </HairlineCard>
        <HairlineCard padding="md" className="space-y-3">
          <h3 className="text-h4">Share</h3>
          <Button variant="secondary" onClick={() => void handleShare()} className="min-h-[44px]">
            Create share link
          </Button>
          {shareMessage ? <p className="text-caption text-muted-foreground">{shareMessage}</p> : null}
        </HairlineCard>
      </div>

      <div className="text-center">
        <Link href="/saas-revenue-leakage-calculator/methodology" className="text-small text-muted-foreground underline">
          Read the methodology
        </Link>
      </div>
    </div>
  );
}
