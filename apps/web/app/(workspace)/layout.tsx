import { WorkspaceNav } from "@/components/workspace-nav";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <WorkspaceNav />
      <main>{children}</main>
    </>
  );
}
