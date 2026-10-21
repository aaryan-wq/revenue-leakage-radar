import { Suspense } from "react";

import { AuditAuthBridge } from "@/components/audit/audit-auth-bridge";
import { AuditFunnelActionsProvider } from "@/components/audit/audit-funnel-actions";
import { AuditFunnelProgress } from "@/components/audit/audit-funnel-progress";
import { WorkspaceLegalFooter } from "@/components/legal/workspace-legal-footer";

export default function AuditLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuditFunnelActionsProvider>
      <AuditAuthBridge />
      <Suspense fallback={<header className="sticky top-0 z-50 h-16 border-b border-line bg-background" />}>
        <AuditFunnelProgress />
      </Suspense>
      <main>{children}</main>
      <WorkspaceLegalFooter />
    </AuditFunnelActionsProvider>
  );
}
