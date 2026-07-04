import { WorkspaceNav } from "@/components/workspace-nav";
import { WorkspaceLegalFooter } from "@/components/legal/workspace-legal-footer";
import { WorkspaceWarmCache } from "@/components/workspace/workspace-warm-cache";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <WorkspaceWarmCache />
      <WorkspaceNav />
      <main>{children}</main>
      <WorkspaceLegalFooter />
    </>
  );
}
