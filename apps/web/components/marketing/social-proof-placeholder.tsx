import { Reveal } from "@/components/motion";

const PLACEHOLDER_LOGOS = ["Series B SaaS", "PE-Backed", "Enterprise", "Growth Stage"] as const;

export function SocialProofPlaceholder() {
  return (
    <section className="mx-auto max-w-marketing px-6 py-20 md:px-10">
      <Reveal>
        <p className="text-center text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">
          Trusted by finance teams
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-6">
          {PLACEHOLDER_LOGOS.map((label) => (
            <div
              key={label}
              className="rounded-lg border border-dashed border-line px-8 py-4 text-sm text-muted-foreground"
            >
              {label}
            </div>
          ))}
        </div>
        <p className="mt-6 text-center text-xs text-muted-foreground">
          Customer logos and case studies coming soon.
        </p>
      </Reveal>
    </section>
  );
}
