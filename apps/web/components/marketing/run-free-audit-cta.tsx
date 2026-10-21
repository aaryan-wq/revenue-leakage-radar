"use client";

import Link from "next/link";
import { AnalyticsEvents } from "@rlr/shared";

import { WORKSPACE_UPLOAD_HREF } from "@/lib/audit-session";
import { captureEvent } from "@/lib/analytics/client";
import { cn } from "@/lib/utils";

interface RunFreeAuditCtaProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  showArrow?: boolean;
  fromWorkspace?: boolean;
  analyticsSource?: string;
  label?: string;
}

const sizeClasses = {
  sm: "h-8 px-3 text-sm",
  md: "h-10 px-4 text-sm",
  lg: "h-10 px-5 text-sm",
};

export function RunFreeAuditCta({
  size = "md",
  className,
  showArrow = true,
  fromWorkspace = false,
  analyticsSource,
  label = "Run Free Audit",
}: RunFreeAuditCtaProps) {
  return (
    <Link
      href={fromWorkspace ? WORKSPACE_UPLOAD_HREF : "/upload"}
      className={cn("inline-flex", className)}
      onClick={() => {
        captureEvent(AnalyticsEvents.FREE_AUDIT_CTA_CLICKED, {
          ...(analyticsSource ? { source: analyticsSource } : {}),
        });
        if (analyticsSource?.startsWith("demo")) {
          captureEvent(AnalyticsEvents.DEMO_CTA_CLICKED, { source: analyticsSource });
        }
      }}
    >
      <span
        className={cn(
          "inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary font-medium text-primary-foreground transition-colors hover:brightness-110",
          sizeClasses[size],
        )}
      >
        {label}
        {showArrow ? <span aria-hidden="true">→</span> : null}
      </span>
    </Link>
  );
}
