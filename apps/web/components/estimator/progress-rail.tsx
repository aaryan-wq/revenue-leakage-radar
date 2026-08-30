"use client";

import { motion, useReducedMotion } from "framer-motion";

import { easedCompletionPercent } from "@/lib/estimator/progress";

interface ProgressRailProps {
  sectionLabel: string | null;
  completionRate: number;
}

export function ProgressRail({ sectionLabel, completionRate }: ProgressRailProps) {
  const reducedMotion = useReducedMotion();
  const percent = easedCompletionPercent(completionRate);

  return (
    <div className="sticky top-[72px] z-40 border-b border-border/40 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto max-w-marketing px-6 md:px-10">
        <div className="flex h-10 items-center justify-between gap-4">
          <p className="truncate text-caption text-muted-foreground">{sectionLabel ?? "Getting started"}</p>
          <p className="shrink-0 text-caption tabular-nums text-muted-foreground">{Math.round(percent)}%</p>
        </div>
        <div className="h-1 w-full overflow-hidden rounded-full bg-border/30">
          <motion.div
            className="h-full rounded-full bg-primary"
            initial={false}
            animate={{ width: `${percent}%` }}
            transition={reducedMotion ? { duration: 0.15 } : { duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
          />
        </div>
      </div>
    </div>
  );
}
