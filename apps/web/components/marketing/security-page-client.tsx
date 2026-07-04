"use client";

import Link from "next/link";
import { Check, FileText, Lock, Mail, Server, Shield, Trash2 } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { SecurityPageTracker } from "@/components/analytics/marketing-page-tracker";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { HairlineCard } from "@/components/ui/hairline-card";

const SUPPORT_EMAIL =
  process.env.SUPPORT_EMAIL ?? process.env.NEXT_PUBLIC_SUPPORT_EMAIL ?? "contact@paevo.co";

const SECTIONS: { icon: LucideIcon; title: string; body: string }[] = [
  {
    icon: Lock,
    title: "Encrypted in transit",
    body: "All uploads and API traffic use HTTPS/TLS. Data in transit is encrypted end to end between your browser and our infrastructure.",
  },
  {
    icon: Trash2,
    title: "Temporary processing",
    body: "Raw CSV files exist only during active processing. They are automatically deleted after ingestion completes or when the audit session expires.",
  },
  {
    icon: Server,
    title: "No persistent storage during free audits",
    body: "Free audit sessions do not retain raw uploads beyond what is required to produce your summary. You retain full ownership of your data at all times.",
  },
  {
    icon: Shield,
    title: "Customer retains ownership",
    body: "Your billing and CRM data belongs to you. We process it solely to deliver audit results. Purchased reports store normalized findings, never original CSV filenames as business logic inputs.",
  },
  {
    icon: FileText,
    title: "SOC 2 roadmap",
    body: "We are building toward SOC 2 Type II certification. A security questionnaire is available upon request for procurement and vendor review.",
  },
];

export function SecurityPageClient() {
  return (
    <>
      <SecurityPageTracker />
      <div className="mx-auto max-w-reading px-6 py-28 md:px-10">
        <Reveal>
          <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">Security</p>
          <h1 className="mt-4 font-heading text-[clamp(2rem,4.5vw,3.4rem)] leading-[1.02] tracking-tight text-balance">
            Built for sensitive billing and CRM data.
          </h1>
          <p className="mt-4 leading-relaxed text-muted-foreground">
            Finance teams trust us with invoice exports, subscription records, pricing catalogs, and CRM contracts.
            Security is not a feature. It is the foundation.
          </p>
        </Reveal>

        <Stagger className="mt-16 space-y-6">
          {SECTIONS.map((section) => (
            <StaggerItem key={section.title}>
              <HairlineCard padding="md">
                <div className="flex items-center gap-3">
                  <section.icon className="h-6 w-6 text-primary" strokeWidth={1.75} />
                  <h2 className="font-heading text-xl tracking-tight">{section.title}</h2>
                </div>
                <p className="mt-4 leading-relaxed text-muted-foreground">{section.body}</p>
              </HairlineCard>
            </StaggerItem>
          ))}

          <StaggerItem>
            <HairlineCard padding="md">
              <div className="flex items-center gap-3">
                <Check className="h-6 w-6 text-primary" strokeWidth={1.75} />
                <h2 className="font-heading text-xl tracking-tight">Automatic deletion after processing</h2>
              </div>
              <p className="mt-4 leading-relaxed text-muted-foreground">
                Canonical normalized records and audit metadata are retained only to support purchased
                reports and your workspace history. Raw CSV uploads are never kept longer than required
                for processing.
              </p>
            </HairlineCard>
          </StaggerItem>

          <StaggerItem>
            <HairlineCard padding="md">
              <div className="flex items-center gap-3">
                <Mail className="h-6 w-6 text-primary" strokeWidth={1.75} />
                <h2 className="font-heading text-xl tracking-tight">Security questionnaire</h2>
              </div>
              <p className="mt-4 text-muted-foreground">
                Need documentation for vendor review? Email{" "}
                <a
                  href={`mailto:${SUPPORT_EMAIL}`}
                  className="text-primary underline-offset-4 hover:underline"
                >
                  {SUPPORT_EMAIL}
                </a>{" "}
                or{" "}
                <Link href="/contact" className="text-primary underline-offset-4 hover:underline">
                  contact us
                </Link>
                .
              </p>
            </HairlineCard>
          </StaggerItem>
        </Stagger>

        <Reveal delay={0.1} className="mt-16">
          <RunFreeAuditCta size="md" />
        </Reveal>
      </div>
    </>
  );
}
