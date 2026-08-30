"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { LiveProfilePanel } from "@/components/estimator/live-profile-panel";
import { ProgressRail } from "@/components/estimator/progress-rail";
import { QuestionStep } from "@/components/estimator/question-step";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { captureEvent } from "@/lib/analytics/client";
import {
  calculateAssessment,
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

  const arrUsd = useMemo(() => {
    const arr = answers["profile.arr_amount"];
    return typeof arr === "number" ? arr : undefined;
  }, [answers]);

  const refresh = useCallback(async (id: string) => {
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
      router.push(`/saas-revenue-leakage-calculator/result/${id}`);
    }
  }, [router]);

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

  const handleCalculate = async () => {
    if (!assessmentId) return;
    setSubmitting(true);
    try {
      await calculateAssessment(assessmentId);
      captureEvent(AnalyticsEvents.ESTIMATOR_COMPLETED, { assessment_id: assessmentId });
      router.push(`/saas-revenue-leakage-calculator/result/${assessmentId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Calculation failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <PageLoadingSkeleton message="Loading assessment…" />;

  return (
    <div className="mx-auto grid max-w-marketing gap-8 px-6 py-12 md:grid-cols-[1fr_320px] md:px-10">
      <div className="space-y-8">
        <ProgressRail
          sections={sections}
          currentSection={currentSection}
          estimatedSecondsRemaining={progress.estimated_seconds_remaining}
        />
        {question ? (
          <QuestionStep
            question={question}
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
          <button
            type="button"
            onClick={() => void handleCalculate()}
            className="rounded-xl bg-primary px-6 py-3 text-body text-primary-foreground min-h-[44px]"
          >
            {submitting ? "Calculating..." : "Calculate my estimate"}
          </button>
        ) : null}
      </div>
      <LiveProfilePanel arrUsd={arrUsd} complexity={complexity} />
    </div>
  );
}
