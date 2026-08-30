"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { LiveProfilePanel } from "@/components/estimator/live-profile-panel";
import { ProgressRail } from "@/components/estimator/progress-rail";
import { QuestionStep } from "@/components/estimator/question-step";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { captureEvent } from "@/lib/analytics/client";
import {
  calculateAssessment,
  clearAssessmentSession,
  createAssessment,
  fetchAssessment,
  fetchQuestionnaire,
  getStoredAssessmentId,
  patchAnswers,
  storeAssessmentSession,
  validateAssessment,
} from "@/lib/estimator/api";
import { AnalyticsEvents, type EstimatorComplexityPreview, type EstimatorQuestion } from "@rlr/shared";

export function EstimatorQuestionnaireClient() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [sections, setSections] = useState<{ id: string; label: string }[]>([]);
  const [question, setQuestion] = useState<EstimatorQuestion | null>(null);
  const [answers, setAnswers] = useState<Record<string, unknown>>({});
  const [progress, setProgress] = useState({
    visible_count: 0,
    answered_count: 0,
    completion_rate: 0,
    estimated_seconds_remaining: 120,
    is_complete: false,
  });
  const [currentSection, setCurrentSection] = useState<string | null>("profile");
  const [complexity, setComplexity] = useState<EstimatorComplexityPreview | null>(null);
  const [draftValue, setDraftValue] = useState<unknown>(null);
  const [currency, setCurrency] = useState("USD");

  const sectionLabel = useMemo(() => {
    const match = sections.find((section) => section.id === currentSection);
    return match?.label ?? "Assessment";
  }, [sections, currentSection]);

  const arrUsd = useMemo(() => {
    const arr = answers["profile.arr_amount"];
    return typeof arr === "number" ? arr : undefined;
  }, [answers]);

  const finishAssessment = useCallback(
    async (id: string) => {
      setCalculating(true);
      setError(null);
      try {
        await calculateAssessment(id);
        captureEvent(AnalyticsEvents.ESTIMATOR_COMPLETED, { assessment_id: id });
        router.push(`/saas-revenue-leakage-calculator/result/${id}`);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to calculate your estimate");
        setCalculating(false);
      }
    },
    [router],
  );

  const refresh = useCallback(
    async (id: string) => {
      const state = await fetchAssessment(id);
      setAnswers(state.answers);
      setQuestion(state.next_question);
      setProgress(state.progress);
      setCurrentSection(state.current_section);
      setComplexity(state.complexity_preview ?? null);
      if (state.next_question) {
        setDraftValue(state.answers[state.next_question.id] ?? null);
      }
      if (state.progress.is_complete) {
        await finishAssessment(id);
      }
    },
    [finishAssessment],
  );

  useEffect(() => {
    async function init() {
      try {
        const questionnaire = await fetchQuestionnaire();
        setSections(questionnaire.sections);
        let id = getStoredAssessmentId();
        if (!id) {
          const created = await createAssessment();
          id = created.assessment_id;
          storeAssessmentSession(created.assessment_id, created.session_token);
          captureEvent(AnalyticsEvents.ESTIMATOR_STARTED, { assessment_id: id });
        }
        if (!id) {
          throw new Error("Unable to create assessment session");
        }
        setAssessmentId(id);
        await refresh(id);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to start assessment");
      } finally {
        setLoading(false);
      }
    }
    void init();
  }, [refresh]);

  const handleContinue = async () => {
    if (!assessmentId || !question) return;
    setSubmitting(true);
    setError(null);
    try {
      const payload: {
        question_id: string;
        value_numeric?: number;
        value_boolean?: boolean;
        value_enum?: string;
        value_text?: string;
        value_json?: string[];
      } = { question_id: question.id };

      if (question.type === "boolean") payload.value_boolean = Boolean(draftValue);
      else if (question.type === "select") payload.value_enum = String(draftValue);
      else if (question.type === "multiselect") payload.value_json = draftValue as string[];
      else if (question.type === "number") payload.value_numeric = Number(draftValue);
      else if (question.type === "currency") {
        payload.value_numeric = Number(draftValue);
        payload.value_text = currency;
      } else if (question.type === "scale") payload.value_numeric = Number(draftValue);

      await patchAnswers(assessmentId, [payload]);
      captureEvent(AnalyticsEvents.QUESTION_ANSWERED, {
        assessment_id: assessmentId,
        question_id: question.id,
      });

      const validation = await validateAssessment(assessmentId);
      if (validation.contradictions.length > 0) {
        setError(validation.contradictions[0]?.message ?? "Please review your answers");
        setSubmitting(false);
        return;
      }

      await refresh(assessmentId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save answer");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <PageLoadingSkeleton message="Preparing your assessment…" />;

  if (calculating) {
    return (
      <>
        <ProgressRail sectionLabel="Calculating" completionRate={1} />
        <PageLoadingSkeleton message="Running your estimate…" />
      </>
    );
  }

  return (
    <>
      <ProgressRail sectionLabel={sectionLabel} completionRate={progress.completion_rate} />
      <div className="mx-auto grid min-h-[calc(100vh-8rem)] max-w-marketing gap-10 px-6 py-12 md:grid-cols-[minmax(0,1fr)_280px] md:px-10 md:py-16">
        <div className="min-w-0">
          {question ? (
            <QuestionStep
              question={question}
              sectionLabel={sectionLabel}
              value={draftValue}
              currency={currency}
              onChange={(val, cur) => {
                setDraftValue(val);
                if (cur) setCurrency(cur);
              }}
              onContinue={handleContinue}
              isSubmitting={submitting}
              error={error}
            />
          ) : progress.is_complete ? (
            <HairlineCard padding="lg" className="mx-auto max-w-readable space-y-4 text-center">
              <p className="text-body text-muted-foreground">Your answers are complete.</p>
              <Button
                onClick={() => assessmentId && void finishAssessment(assessmentId)}
                disabled={submitting}
                className="min-h-[44px]"
              >
                Calculate my estimate
              </Button>
              {error ? <p className="text-small text-destructive">{error}</p> : null}
            </HairlineCard>
          ) : error ? (
            <HairlineCard padding="lg" className="mx-auto max-w-readable space-y-4 text-center">
              <p className="text-body text-destructive">{error}</p>
              <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
                <Button variant="secondary" onClick={() => window.location.reload()} className="min-h-[44px]">
                  Try again
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => {
                    clearAssessmentSession();
                    window.location.href = "/saas-revenue-leakage-calculator/start";
                  }}
                  className="min-h-[44px]"
                >
                  Start over
                </Button>
              </div>
            </HairlineCard>
          ) : null}
        </div>
        <LiveProfilePanel arrUsd={arrUsd} complexity={complexity} />
      </div>
    </>
  );
}
