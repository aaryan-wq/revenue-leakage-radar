"use client";

import { Reveal } from "@/components/motion";
import { PrivacyContent } from "@/components/legal/privacy-content";
import { SiteFooter } from "@/components/site-footer";
import { HairlineCard } from "@/components/ui/hairline-card";

export default function PrivacyPage() {
  return (
    <>
      <main className="mx-auto max-w-reading px-6 py-28 md:px-10">
        <Reveal>
          <h1 className="font-heading text-[clamp(2rem,4.5vw,3.4rem)] leading-[1.02] tracking-tight text-balance">
            Privacy Policy
          </h1>
          <p className="mt-4 text-sm text-muted-foreground">Last updated: July 2, 2026</p>
        </Reveal>

        <Reveal delay={0.1} className="mt-12">
          <HairlineCard padding="md">
            <PrivacyContent />
          </HairlineCard>
        </Reveal>
      </main>
      <SiteFooter />
    </>
  );
}
