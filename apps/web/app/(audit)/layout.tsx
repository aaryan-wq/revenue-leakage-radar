import { AuditFunnelProgress } from "@/components/audit/audit-funnel-progress";

export default function AuditLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <AuditFunnelProgress />
      <main>{children}</main>
    </>
  );
}
