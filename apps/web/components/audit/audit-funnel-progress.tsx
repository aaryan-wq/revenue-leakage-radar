"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

const STEPS = [
  { href: "/upload", label: "Upload" },
  { href: "/validation", label: "Validation" },
  { href: "/analysis", label: "Analysis" },
  { href: "/summary", label: "Summary" },
] as const;

function stepIndex(pathname: string): number {
  if (pathname.startsWith("/summary")) return 3;
  if (pathname.startsWith("/analysis")) return 2;
  if (pathname.startsWith("/validation")) return 1;
  if (pathname.startsWith("/upload")) return 0;
  return 0;
}

export function AuditFunnelProgress() {
  const pathname = usePathname();
  const current = stepIndex(pathname);
  const progressPercent = ((current + 1) / STEPS.length) * 100;

  return (
    <header className="sticky top-0 z-50 border-b border-line/60">
      <div className="absolute inset-0 -z-10 bg-background/85 backdrop-blur-xl" />
      <div className="mx-auto max-w-marketing px-6 md:px-10">
        <div className="flex h-14 items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <span className="h-2 w-2 rounded-full bg-primary" />
            <span className="font-heading text-[0.95rem] tracking-tight">Radar</span>
          </Link>
          <Link
            href="/"
            className="text-[0.78rem] text-muted-foreground transition-colors hover:text-foreground"
          >
            Exit audit
          </Link>
        </div>

        <div className="pb-4">
          <div className="relative h-1 overflow-hidden rounded-full bg-line">
            <motion.div
              className="absolute inset-y-0 left-0 rounded-full bg-primary"
              initial={false}
              animate={{ width: `${progressPercent}%` }}
              transition={{ type: "spring", stiffness: 120, damping: 24 }}
            />
          </div>

          <ol className="mt-4 flex items-center justify-between gap-2">
            {STEPS.map((step, index) => {
              const isComplete = index < current;
              const isCurrent = index === current;
              const isFuture = index > current;

              return (
                <li key={step.href} className="flex min-w-0 flex-1 flex-col items-center gap-1.5">
                  <span
                    className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[0.65rem] font-medium tnum transition-colors ${
                      isComplete
                        ? "bg-primary text-primary-foreground"
                        : isCurrent
                          ? "border-2 border-primary bg-background text-foreground"
                          : "border border-line bg-background text-muted-foreground"
                    }`}
                  >
                    {isComplete ? "✓" : index + 1}
                  </span>
                  <span
                    className={`truncate text-[0.68rem] uppercase tracking-[0.12em] ${
                      isCurrent ? "text-foreground" : isFuture ? "text-muted-foreground/60" : "text-muted-foreground"
                    }`}
                  >
                    {step.label}
                  </span>
                </li>
              );
            })}
          </ol>
        </div>
      </div>
    </header>
  );
}
