import Link from "next/link";
import { Lock, Shield, Trash2 } from "lucide-react";

import { Reveal } from "@/components/motion";
import { HairlineCard } from "@/components/ui/hairline-card";

const POINTS = [
  { icon: Lock, text: "Encrypted in transit (HTTPS/TLS)" },
  { icon: Trash2, text: "Temporary processing. Raw CSVs deleted after ingestion" },
  { icon: Shield, text: "No persistent storage during free audits" },
] as const;

export function SecuritySummary() {
  return (
    <section className="border-t border-line bg-field">
      <div className="mx-auto max-w-marketing px-6 py-14 md:px-10 md:py-20">
        <Reveal>
          <h2 className="text-h2 max-w-xl text-balance text-foreground">
            Your billing and CRM data stays yours.
          </h2>
        </Reveal>

        <div className="mt-8 grid gap-3 sm:mt-10 sm:gap-4 md:grid-cols-3">
          {POINTS.map(({ icon: Icon, text }) => (
            <HairlineCard key={text} padding="none" className="p-5 md:p-8">
              <Icon className="h-5 w-5 text-primary" strokeWidth={1.75} />
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{text}</p>
            </HairlineCard>
          ))}
        </div>

        <Reveal delay={0.1} className="mt-8 space-y-3">
          <p className="max-w-reading text-sm leading-relaxed text-muted-foreground">
            Names and emails are optional. You can blank them before upload if that feels better.{" "}
            <Link
              href="/security#anonymize-before-upload"
              className="font-medium text-primary underline-offset-4 hover:underline"
            >
              How to anonymize safely
            </Link>
          </p>
          <Link
            href="/security"
            className="inline-block text-sm font-medium text-primary underline-offset-4 hover:underline"
          >
            Read full security overview →
          </Link>
        </Reveal>
      </div>
    </section>
  );
}
