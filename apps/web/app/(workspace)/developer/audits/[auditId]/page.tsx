import { DeveloperAuditDetail } from "@/components/developer/developer-audit-detail";

export default async function DeveloperAuditDetailPage({
  params,
}: {
  params: Promise<{ auditId: string }>;
}) {
  const { auditId } = await params;
  return <DeveloperAuditDetail auditId={auditId} />;
}
