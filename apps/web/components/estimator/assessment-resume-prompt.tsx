"use client";

import { ArrowRight, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import type { EstimatorResumeState } from "@rlr/shared";

interface AssessmentResumePromptProps {
  resume: EstimatorResumeState;
  onContinue: () => void;
  onViewPrevious?: () => void;
}

export function AssessmentResumePrompt({
  resume,
  onContinue,
  onViewPrevious,
}: AssessmentResumePromptProps) {
  const count = resume.pending_count;
  const questionLabel = count === 1 ? "question" : "questions";

  return (
    <HairlineCard padding="lg" className="mx-auto max-w-readable space-y-6 text-center">
      <div className="space-y-3">
        <p className="text-overline text-muted-foreground">
          {resume.requires_reanswer ? "Assessment update" : "Welcome back"}
        </p>
        <h1 className="text-h3 text-foreground">
          {resume.requires_reanswer ? "New questions available" : "Pick up where you left off"}
        </h1>
        <p className="text-body text-muted-foreground">
          {resume.requires_reanswer
            ? `We updated the questionnaire with ${count} new ${questionLabel}. Answer them to refresh your estimate, or keep viewing your previous results.`
            : `You have ${count} remaining ${questionLabel}. Continue to refine your estimate.`}
        </p>
      </div>
      <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
        <Button onClick={onContinue} className="min-h-[44px] gap-2">
          {resume.requires_reanswer ? "Answer new questions" : "Continue assessment"}
          <ArrowRight className="size-4" aria-hidden />
        </Button>
        {resume.requires_reanswer && onViewPrevious ? (
          <Button variant="secondary" onClick={onViewPrevious} className="min-h-[44px] gap-2">
            <RotateCcw className="size-4" aria-hidden />
            View previous estimate
          </Button>
        ) : null}
      </div>
    </HairlineCard>
  );
}

interface AssessmentResumeBannerProps {
  resume: EstimatorResumeState;
  onAnswer: () => void;
}

export function AssessmentResumeBanner({ resume, onAnswer }: AssessmentResumeBannerProps) {
  if (!resume.requires_reanswer) return null;

  const count = resume.pending_count;
  const questionLabel = count === 1 ? "question" : "questions";

  return (
    <HairlineCard padding="md" className="mb-8 border-primary/20 bg-surface-glass-subtle">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-overline text-muted-foreground">Questionnaire updated</p>
          <p className="text-body mt-2 text-foreground">
            {count} new {questionLabel} can improve your estimate accuracy.
          </p>
        </div>
        <Button variant="secondary" onClick={onAnswer} className="min-h-[44px] shrink-0">
          Answer new questions
        </Button>
      </div>
    </HairlineCard>
  );
}
