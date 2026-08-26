"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { AnalyticsEvents } from "@rlr/shared";

import { captureEvent } from "@/lib/analytics/client";
import { cn } from "@/lib/utils";

interface ViewSampleReportCtaProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  analyticsSource?: string;
}

const sizeClasses = {
  sm: "h-9 px-4 text-[0.8rem]",
  md: "px-6 py-3.5 text-[0.92rem]",
  lg: "px-7 py-4 text-[0.95rem]",
};

export function ViewSampleReportCta({
  size = "md",
  className,
  analyticsSource = "hero",
}: ViewSampleReportCtaProps) {
  return (
    <Link
      href="/demo"
      className={cn("inline-flex", className)}
      onClick={() =>
        captureEvent(AnalyticsEvents.DEMO_CTA_CLICKED, {
          source: analyticsSource,
          destination: "demo_report",
        })
      }
    >
      <motion.span
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={cn(
          "inline-flex items-center gap-2 rounded-full border border-line bg-card/80 font-medium text-foreground backdrop-blur-sm transition-colors hover:bg-secondary",
          sizeClasses[size],
        )}
      >
        View sample report
      </motion.span>
    </Link>
  );
}
