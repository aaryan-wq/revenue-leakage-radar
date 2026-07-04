"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { AnalyticsEvents } from "@rlr/shared";

import { WORKSPACE_UPLOAD_HREF } from "@/lib/audit-session";
import { captureEvent } from "@/lib/analytics/client";
import { cn } from "@/lib/utils";

interface RunFreeAuditCtaProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  showArrow?: boolean;
  fromWorkspace?: boolean;
}

const sizeClasses = {
  sm: "h-9 px-4 text-[0.8rem]",
  md: "px-6 py-3.5 text-[0.92rem]",
  lg: "px-7 py-4 text-[0.95rem]",
};

export function RunFreeAuditCta({
  size = "md",
  className,
  showArrow = true,
  fromWorkspace = false,
}: RunFreeAuditCtaProps) {
  return (
    <Link
      href={fromWorkspace ? WORKSPACE_UPLOAD_HREF : "/upload"}
      className={cn("inline-flex", className)}
      onClick={() => captureEvent(AnalyticsEvents.FREE_AUDIT_CTA_CLICKED)}
    >
      <motion.span
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={cn(
          "group inline-flex items-center gap-2 rounded-full bg-primary font-medium text-primary-foreground shadow-[0_12px_40px_-10px] shadow-primary/40 transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50",
          sizeClasses[size],
        )}
      >
        Run Free Audit
        {showArrow && (
          <span className="transition-transform duration-300 group-hover:translate-x-0.5">→</span>
        )}
      </motion.span>
    </Link>
  );
}
