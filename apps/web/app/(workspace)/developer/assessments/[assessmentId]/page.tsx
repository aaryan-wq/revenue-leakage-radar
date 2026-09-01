import { DeveloperAssessmentDetail } from "@/components/developer/developer-assessment-detail";

export default async function DeveloperAssessmentDetailPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = await params;
  return <DeveloperAssessmentDetail assessmentId={assessmentId} />;
}
