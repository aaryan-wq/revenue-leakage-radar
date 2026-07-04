"use client";

import Link from "next/link";
import { ArrowRight, HelpCircle, Mail, Shield, Workflow } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { Reveal } from "@/components/motion";
import { buttonVariants } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/hairline-card";
import { cn } from "@/lib/utils";

const HELP_ACTIONS: {
  href: string;
  label: string;
  description: string;
  icon: LucideIcon;
}[] = [
  {
    href: "/faq",
    label: "FAQ",
    description: "Answers on audits, uploads, verification checks, and unlocking reports.",
    icon: HelpCircle,
  },
  {
    href: "/contact",
    label: "Contact support",
    description: "Reach our team for audit questions, billing issues, or security reviews.",
    icon: Mail,
  },
  {
    href: "/how-it-works",
    label: "How it works",
    description: "From CSV upload to recoverable revenue: the full audit workflow.",
    icon: Workflow,
  },
  {
    href: "/security",
    label: "Security overview",
    description: "How we handle uploads, encryption, retention, and data isolation.",
    icon: Shield,
  },
];

export function HelpPageClient() {
  return (
    <div className="mx-auto max-w-reading px-6 py-12 md:px-10">
      <Reveal>
        <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">Help</p>
        <h1 className="mt-2 font-heading text-3xl tracking-tight">How can we help?</h1>
        <p className="mt-4 leading-relaxed text-muted-foreground">
          Guides, support, and product context for running audits and interpreting your results.
        </p>
      </Reveal>

      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        {HELP_ACTIONS.map((action, index) => {
          const Icon = action.icon;
          return (
            <Reveal key={action.href} delay={index * 0.05}>
              <HairlineCard padding="md" className="flex h-full flex-col">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Icon className="h-5 w-5" strokeWidth={1.75} />
                </div>
                <h2 className="mt-4 font-heading text-lg tracking-tight">{action.label}</h2>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-muted-foreground">
                  {action.description}
                </p>
                <Link
                  href={action.href}
                  className={cn(
                    buttonVariants({ variant: "secondary", size: "md" }),
                    "mt-6 w-full justify-between",
                  )}
                >
                  {action.label}
                  <ArrowRight className="h-4 w-4" strokeWidth={1.75} />
                </Link>
              </HairlineCard>
            </Reveal>
          );
        })}
      </div>
    </div>
  );
}
