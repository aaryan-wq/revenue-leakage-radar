"use client";

import Link from "next/link";
import { motion } from "framer-motion";

import { cn } from "@/lib/utils";

interface RunFreeAuditCtaProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  showArrow?: boolean;
}

const sizeClasses = {
  sm: "px-4 py-2 text-[0.8rem]",
  md: "px-6 py-3.5 text-[0.92rem]",
  lg: "px-7 py-4 text-[0.95rem]",
};

export function RunFreeAuditCta({
  size = "md",
  className,
  showArrow = true,
}: RunFreeAuditCtaProps) {
  return (
    <Link href="/upload" className={cn("inline-flex", className)}>
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
