"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/page-loading";
import { DeveloperDetailField, DeveloperDetailSection } from "@/components/developer/developer-detail-field";
import { getAdminAssessmentDetail } from "@/lib/admin-api";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { formatDeveloperTimestamp, formatDeveloperValue } from "@/lib/developer-format";
import { queryKeys } from "@/lib/query/keys";
import { formatCurrency } from "@rlr/shared";

function formatArr(amount: string | null, currency: string | null): string {
  if (!amount) return "—";
  const formatted = formatCurrency(amount);
  return currency ? `${formatted} ${currency}` : formatted;
}

export function DeveloperAssessmentDetail({ assessmentId }: { assessmentId: string }) {
  const { getToken } = useAppAuth();

  const assessmentQuery = useQuery({
    queryKey: queryKeys.adminAssessment(assessmentId),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new ApiError("Authentication required.", 401);
      return getAdminAssessmentDetail(token, assessmentId);
    },
  });

  if (assessmentQuery.isLoading) {
    return <PageLoadingSkeleton message="Loading assessment details…" variant="list" />;
  }

  if (assessmentQuery.error || !assessmentQuery.data) {
    const message =
      assessmentQuery.error instanceof ApiError
        ? assessmentQuery.error.message
        : "Unable to load assessment.";
    return (
      <div className="rounded-2xl border border-line/60 bg-secondary/30 p-8 text-center">
        <p className="text-muted-foreground">{message}</p>
        <div className="mt-4 flex justify-center gap-3">
          <Link href="/developer/assessments" className={buttonVariants({ variant: "secondary" })}>
            Back to assessments
          </Link>
          <Button onClick={() => void assessmentQuery.refetch()}>Retry</Button>
        </div>
      </div>
    );
  }

  const assessment = assessmentQuery.data;
  const title =
    assessment.lead_company_name ??
    assessment.lead_email ??
    assessment.industry ??
    "Assessment detail";

  const answersBySection = assessment.answers.reduce<Record<string, typeof assessment.answers>>(
    (groups, answer) => {
      const section = answer.section;
      if (!groups[section]) groups[section] = [];
      groups[section].push(answer);
      return groups;
    },
    {},
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link
            href="/developer/assessments"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Back to assessments
          </Link>
          <h1 className="mt-2 font-heading text-2xl tracking-tight">{title}</h1>
          <p className="mt-1 font-mono text-xs text-muted-foreground">{assessment.assessment_id}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="gray">{assessment.status}</Badge>
          {assessment.scan_intent && <Badge variant="elevated">Scan intent</Badge>}
          {assessment.lead_score != null && assessment.lead_score > 0 && (
            <Badge variant="gray">Score {assessment.lead_score}</Badge>
          )}
        </div>
      </div>

      <GlassCard className="space-y-8 p-8">
        <DeveloperDetailSection title="Overview">
          <dl className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <DeveloperDetailField
              label="Estimated leakage"
              value={
                assessment.estimated_leakage
                  ? formatCurrency(assessment.estimated_leakage)
                  : "—"
              }
            />
            <DeveloperDetailField
              label="ARR"
              value={formatArr(assessment.arr_amount, assessment.arr_currency)}
            />
            <DeveloperDetailField label="Industry" value={formatDeveloperValue(assessment.industry)} />
            <DeveloperDetailField label="Country" value={formatDeveloperValue(assessment.country)} />
            <DeveloperDetailField
              label="Company type"
              value={formatDeveloperValue(assessment.company_type)}
            />
            <DeveloperDetailField
              label="Customers"
              value={formatDeveloperValue(assessment.customer_count)}
            />
            <DeveloperDetailField
              label="Started"
              value={formatDeveloperTimestamp(assessment.started_at)}
            />
            <DeveloperDetailField
              label="Completed"
              value={formatDeveloperTimestamp(assessment.completed_at)}
            />
            <DeveloperDetailField
              label="Questionnaire version"
              value={assessment.questionnaire_version}
            />
          </dl>
        </DeveloperDetailSection>

        <DeveloperDetailSection title="Lead">
          <dl className="grid gap-6 sm:grid-cols-2">
            <DeveloperDetailField label="Email" value={formatDeveloperValue(assessment.lead_email)} />
            <DeveloperDetailField
              label="Company"
              value={formatDeveloperValue(assessment.lead_company_name)}
            />
            <DeveloperDetailField label="Role" value={formatDeveloperValue(assessment.lead_role)} />
            <DeveloperDetailField
              label="Linked user"
              value={formatDeveloperValue(assessment.clerk_user_name ?? assessment.clerk_user_email)}
            />
          </dl>
        </DeveloperDetailSection>

        {assessment.linked_audit_id && (
          <DeveloperDetailSection title="Links">
            <Link
              href={`/developer/audits/${assessment.linked_audit_id}`}
              className={buttonVariants({ variant: "secondary" })}
            >
              View linked audit
            </Link>
          </DeveloperDetailSection>
        )}

        <DeveloperDetailSection title="Answers">
          {assessment.answers.length === 0 ? (
            <p className="text-sm text-muted-foreground">No answers recorded yet.</p>
          ) : (
            <div className="space-y-8">
              {Object.entries(answersBySection).map(([section, answers]) => (
                <div key={section} className="space-y-4">
                  <h3 className="text-overline text-muted-foreground">{section}</h3>
                  <div className="space-y-4">
                    {answers.map((answer) => (
                      <div
                        key={answer.question_id}
                        className="rounded-xl border border-line/60 bg-secondary/10 px-4 py-4"
                      >
                        <p className="text-sm font-medium">{answer.label ?? answer.question_id}</p>
                        <p className="mt-2 text-sm text-foreground">{answer.display_value}</p>
                        <p className="mt-2 text-xs text-muted-foreground">
                          {formatDeveloperTimestamp(answer.answered_at)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </DeveloperDetailSection>

        {assessment.result_summary && (
          <DeveloperDetailSection title="Model result">
            <pre className="overflow-x-auto rounded-xl border border-line/60 bg-secondary/20 p-4 text-xs">
              {JSON.stringify(assessment.result_summary, null, 2)}
            </pre>
          </DeveloperDetailSection>
        )}
      </GlassCard>
    </div>
  );
}
