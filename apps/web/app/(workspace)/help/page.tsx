import { WorkspacePlaceholderPage } from "@/components/workspace/workspace-placeholder-page";

const SECTIONS = [
  { title: "Documentation", body: "Step-by-step guides for uploading billing data and interpreting findings." },
  { title: "Support", body: "Email support for audit questions, billing issues, and security reviews." },
  { title: "Changelog", body: "Product updates, new verification rules, and integration releases." },
];

export default function HelpPage() {
  return (
    <WorkspacePlaceholderPage
      title="Help"
      description="Resources for running audits, unlocking reports, and getting the most from your workspace."
      items={SECTIONS}
      links={[
        { href: "/faq", label: "Frequently asked questions" },
        { href: "/contact", label: "Contact support" },
        { href: "/security", label: "Security overview" },
        { href: "/how-it-works", label: "How it works" },
      ]}
    />
  );
}
