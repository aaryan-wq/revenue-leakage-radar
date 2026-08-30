"use client";

import { HairlineCard } from "@/components/ui/glass-card";
import type { EstimatorResumeState } from "@rlr/shared";

export function AssessmentResumeNotice({ resume }: { resume: EstimatorResumeState }) {
  if (!resume.is_resuming || resume.requires_reanswer) return null;

  const count = resume.pending_count;
  const questionLabel = count === 1 ? "question" : "questions";

  return (
    <HairlineCard padding="sm" className="mb-6 border-primary/15 bg-surface-glass-subtle">
      <p className="text-small text-muted-foreground">
        Welcome back. {count} {questionLabel} remaining from your last session.
      </p>
    </HairlineCard>
  );
}
