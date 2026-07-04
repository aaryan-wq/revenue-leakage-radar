"use client";

import Link from "next/link";
import { Mail } from "lucide-react";
import { AnalyticsEvents } from "@rlr/shared";

import { LegalLinks } from "@/components/legal/legal-links";
import { Reveal } from "@/components/motion";
import { HairlineCard } from "@/components/ui/hairline-card";
import { captureEvent } from "@/lib/analytics/client";

interface ContactPageClientProps {
  email: string;
}

export function ContactPageClient({ email }: ContactPageClientProps) {
  return (
    <div className="mx-auto max-w-reading px-6 py-28 md:px-10">
      <Reveal>
        <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">Contact</p>
        <h1 className="mt-4 font-heading text-[clamp(2rem,4.5vw,3.4rem)] leading-[1.02] tracking-tight text-balance">
          We are here to help
        </h1>
        <p className="mt-4 leading-relaxed text-muted-foreground">
          Questions about your audit, billing, or security? Reach out to our team.
        </p>
      </Reveal>

      <Reveal delay={0.1} className="mt-12">
        <HairlineCard padding="lg" className="text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-line bg-secondary/40">
            <Mail className="h-7 w-7 text-primary" strokeWidth={1.75} />
          </div>
          <h2 className="mt-6 font-heading text-2xl tracking-tight">Email Support</h2>
          <p className="mt-3 leading-relaxed text-muted-foreground">
            For billing, technical, or security inquiries, email our team. For recurring audits,
            integrations, and enterprise workspace, ask about our Enterprise plan.
          </p>
          <a
            href={`mailto:${email}`}
            className="mt-8 inline-flex items-center rounded-full bg-primary px-6 py-3.5 text-[0.92rem] font-medium text-primary-foreground transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50"
            onClick={() => {
              captureEvent(AnalyticsEvents.CONTACT_SALES_CLICKED);
              captureEvent(AnalyticsEvents.CONTACT_SALES_SUBMITTED, { channel: "email" });
            }}
          >
            {email}
          </a>
        </HairlineCard>
      </Reveal>

      <Reveal delay={0.15} className="mt-8">
        <p className="text-center text-muted-foreground">
          Looking for quick answers? Visit our{" "}
          <Link href="/faq" className="text-primary underline-offset-4 hover:underline">
            FAQ
          </Link>
          .
        </p>
      </Reveal>

      <Reveal delay={0.2} className="mt-8">
        <LegalLinks className="justify-center" />
      </Reveal>
    </div>
  );
}
