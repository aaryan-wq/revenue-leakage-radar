"use client";

import { useEffect } from "react";
import { Mail } from "lucide-react";
import { AnalyticsEvents } from "@rlr/shared";

import { FeedbackForm } from "@/components/feedback/feedback-form";
import { Reveal } from "@/components/motion";
import { HairlineCard } from "@/components/ui/hairline-card";
import { captureEvent } from "@/lib/analytics/client";
import { FEEDBACK_EMAIL } from "@/lib/feedback-email";

export function FeedbackPageClient() {
  useEffect(() => {
    captureEvent(AnalyticsEvents.FEEDBACK_PAGE_VIEWED);
  }, []);

  return (
    <div className="mx-auto max-w-reading px-6 py-14 md:px-10 md:py-28">
      <Reveal>
        <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">Feedback</p>
        <h1 className="mt-4 font-heading text-[clamp(1.85rem,7vw,3.4rem)] leading-[1.02] tracking-tight text-balance md:text-[clamp(2rem,4.5vw,3.4rem)]">
          We want your feedback
        </h1>
        <p className="mt-4 leading-relaxed text-muted-foreground">
          Paevo is built in the open. Every bug report, idea, and honest reaction helps us ship
          something finance teams can trust. Tell us what is working, what is not, and what you
          wish existed.
        </p>
      </Reveal>

      <Reveal delay={0.1} className="mt-10 md:mt-12">
        <HairlineCard padding="none" className="p-6 md:p-10">
          <h2 className="font-heading text-xl tracking-tight md:text-2xl">Send us a message</h2>
          <p className="mt-2 text-[0.92rem] leading-relaxed text-muted-foreground">
            Your note goes straight to our team, no ticket queue, no black hole.
          </p>
          <FeedbackForm source="page" className="mt-8" />
        </HairlineCard>
      </Reveal>

      <Reveal delay={0.15} className="mt-8">
        <HairlineCard padding="none" className="p-6 text-center md:p-10">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-line bg-secondary/40">
            <Mail className="h-7 w-7 text-primary" strokeWidth={1.75} />
          </div>
          <h2 className="mt-6 font-heading text-xl tracking-tight md:text-2xl">Prefer email?</h2>
          <p className="mt-3 leading-relaxed text-muted-foreground">
            Skip the form and write directly. We read every message.
          </p>
          <a
            href={`mailto:${FEEDBACK_EMAIL}`}
            className="mt-8 inline-flex max-w-full items-center break-all rounded-full bg-primary px-6 py-3.5 text-[0.92rem] font-medium text-primary-foreground transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50"
          >
            {FEEDBACK_EMAIL}
          </a>
        </HairlineCard>
      </Reveal>
    </div>
  );
}
