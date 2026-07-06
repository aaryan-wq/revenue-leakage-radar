import { Suspense } from "react";

import { AuditAuthBridge } from "@/components/audit/audit-auth-bridge";
import { AuditFunnelProgress } from "@/components/audit/audit-funnel-progress";
import { WorkspaceLegalFooter } from "@/components/legal/workspace-legal-footer";

export default function AuditLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <AuditAuthBridge />
      <Suspense fallback={<header className="sticky top-0 z-50 h-[72px] border-b border-line/60 bg-background/85 backdrop-blur-xl" />}>
        <AuditFunnelProgress />
      </Suspense>
      <main>{children}</main>
      <WorkspaceLegalFooter />
    </>
  );
}
