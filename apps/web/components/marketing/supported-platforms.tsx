import { Reveal } from "@/components/motion";

const PLATFORMS = [
  "Stripe",
  "Chargebee",
  "HubSpot",
  "Salesforce",
  "Maxio",
  "Zuora",
  "NetSuite",
  "QuickBooks",
] as const;

interface SupportedPlatformsProps {
  compact?: boolean;
}

export function SupportedPlatforms({ compact = false }: SupportedPlatformsProps) {
  return (
    <section className={compact ? "py-10" : "border-y border-line py-14"}>
      <div className="mx-auto max-w-marketing px-6 md:px-10">
        <Reveal>
          <p className="text-center text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">
            Works with billing and CRM exports from
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
            {PLATFORMS.map((name) => (
              <span
                key={name}
                className="font-heading text-[0.9rem] tracking-tight text-muted-foreground/80"
              >
                {name}
              </span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
