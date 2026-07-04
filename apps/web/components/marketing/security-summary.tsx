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
    <section className="border-t border-line bg-secondary/30">
      <div className="mx-auto max-w-marketing px-6 py-20 md:px-10">
        <Reveal>
          <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            Security
          </p>
          <h2 className="mt-3 max-w-xl font-heading text-[clamp(1.6rem,3.5vw,2.4rem)] leading-[1.05] tracking-tight">
            Your billing and CRM data stays yours.
          </h2>
        </Reveal>

        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {POINTS.map(({ icon: Icon, text }) => (
            <HairlineCard key={text} padding="md">
              <Icon className="h-5 w-5 text-primary" strokeWidth={1.75} />
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{text}</p>
            </HairlineCard>
          ))}
        </div>

        <Reveal delay={0.1} className="mt-8">
          <Link
            href="/security"
            className="text-sm font-medium text-primary underline-offset-4 hover:underline"
          >
            Read full security overview →
          </Link>
        </Reveal>
      </div>
    </section>
  );
}
