"use client";

import Link from "next/link";
import { AnalyticsEvents } from "@rlr/shared";

import { captureEvent } from "@/lib/analytics/client";
import { cn } from "@/lib/utils";

interface ViewSampleReportCtaProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  analyticsSource?: string;
  label?: string;
}

const sizeClasses = {
  sm: "h-8 px-3 text-sm",
  md: "h-10 px-4 text-sm",
  lg: "h-10 px-5 text-sm",
};

export function ViewSampleReportCta({
  size = "md",
  className,
  analyticsSource = "hero",
  label = "View sample report",
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
      <span
        className={cn(
          "inline-flex w-full items-center justify-center gap-2 rounded-lg border border-border bg-background font-medium text-foreground transition-[background-color,transform] duration-fast ease-glide hover:bg-secondary active:scale-[0.98] motion-reduce:transform-none",
          sizeClasses[size],
        )}
      >
        {label}
      </span>
    </Link>
  );
}
