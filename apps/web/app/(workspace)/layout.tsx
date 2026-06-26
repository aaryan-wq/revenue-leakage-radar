import { WorkspaceNav } from "@/components/layout/workspace-nav";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <WorkspaceNav />
      <main>{children}</main>
    </>
  );
}
