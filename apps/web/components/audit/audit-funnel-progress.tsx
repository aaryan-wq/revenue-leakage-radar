"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { useQueryClient } from "@tanstack/react-query";

import { Logo, NAV_LOGO_CLASS, NAV_ROW_CLASS } from "@/components/brand/logo";
import {
  exitAuditFromFunnel,
  getAuditExitHref,
  getAuditExitHrefFromSearch,
  isCompletedAuditPath,
} from "@/lib/audit-session";
import { queryKeys } from "@/lib/query/keys";
import { cn } from "@/lib/utils";

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
  const router = useRouter();
  const queryClient = useQueryClient();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const exitHrefFromUrl = getAuditExitHrefFromSearch(searchParams);
  const [exitHref, setExitHref] = useState(exitHrefFromUrl);
  const current = stepIndex(pathname);
  const progressPercent = ((current + 1) / STEPS.length) * 100;

  useEffect(() => {
    setExitHref(getAuditExitHref());
  }, [exitHrefFromUrl]);

  const handleExit = async () => {
    const fromSummary = isCompletedAuditPath(pathname);
    await exitAuditFromFunnel(pathname);
    if (fromSummary) {
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
    }
    router.push(exitHref);
  };

  return (
    <header className="sticky top-0 z-50 border-b border-line/60">
      <div className="absolute inset-0 -z-10 bg-background/85 backdrop-blur-xl" />
      <div className="mx-auto max-w-marketing px-6 md:px-10">
        <div className={cn("justify-between gap-4", NAV_ROW_CLASS)}>
          <button
            type="button"
            onClick={() => void handleExit()}
            className="inline-flex items-center border-0 bg-transparent p-0"
            aria-label="Exit audit"
          >
            <Logo variant="short" className={NAV_LOGO_CLASS.short} />
          </button>
          <button
            type="button"
            onClick={() => void handleExit()}
            className="inline-flex h-9 items-center text-[0.78rem] text-muted-foreground transition-colors hover:text-foreground"
          >
            Exit audit
          </button>
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
