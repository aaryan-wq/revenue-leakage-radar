import { WorkspacePlaceholderPage } from "@/components/workspace/workspace-placeholder-page";

const ROLES = [
  { title: "Owner", body: "Full workspace access, billing, team management, and account deletion." },
  { title: "Admin", body: "Manage audits, reports, uploads, and team members." },
  { title: "Finance", body: "Run audits, view findings, and export reports." },
  { title: "Viewer", body: "Read-only access to summaries and purchased reports." },
];

export default function TeamPage() {
  return (
    <WorkspacePlaceholderPage
      title="Team"
      description="Invite colleagues to your revenue recovery workspace. Team management with role-based access is coming soon — powered by organization-level authentication."
      items={ROLES}
      links={[
        { href: "/account", label: "Account settings" },
        { href: "/billing", label: "Upgrade for team workspace" },
      ]}
    />
  );
}
