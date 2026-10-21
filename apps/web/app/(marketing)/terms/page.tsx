"use client";

import { Reveal } from "@/components/motion";
import { TermsContent } from "@/components/legal/terms-content";
import { SiteFooter } from "@/components/site-footer";
import { HairlineCard } from "@/components/ui/hairline-card";

export default function TermsPage() {
  return (
    <>
      <div className="bg-field">
        <div className="mx-auto max-w-reading px-6 py-14 md:px-10 md:py-20">
          <Reveal>
            <h1 className="text-h1 text-balance text-foreground">Terms of Service</h1>
            <p className="mt-4 text-sm text-muted-foreground">Last updated: July 2, 2026</p>
          </Reveal>
        </div>
      </div>
      <main className="mx-auto max-w-reading px-6 py-12 md:px-10 md:pb-28">
        <Reveal>
          <HairlineCard padding="none" className="p-5 md:p-8">
            <TermsContent />
          </HairlineCard>
        </Reveal>
      </main>
      <SiteFooter />
    </>
  );
}
