import { WorkspacePlaceholderPage } from "@/components/workspace/workspace-placeholder-page";

const ROADMAP = [
  { title: "Stripe", body: "Direct billing data sync — invoices, subscriptions, and catalog." },
  { title: "Chargebee", body: "Subscription and invoice reconciliation without CSV exports." },
  { title: "HubSpot", body: "CRM contract terms vs. billed amounts." },
  { title: "Salesforce", body: "Opportunity and contract data for renewal verification." },
  { title: "Maxio", body: "Native export pipeline for SaaS billing teams." },
  { title: "Zuora", body: "Enterprise subscription billing integration." },
];

export default function IntegrationsPage() {
  return (
    <WorkspacePlaceholderPage
      title="Integrations"
      description="API integrations are on the roadmap. Today, upload CSV exports from any billing system. Connectors will eliminate manual exports for supported platforms."
      items={ROADMAP}
      links={[{ href: "/upload", label: "Upload CSV exports now" }]}
    />
  );
}
