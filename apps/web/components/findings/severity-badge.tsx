"use client";

import { motion } from "framer-motion";

import type { FindingSeverity } from "@rlr/shared";

import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";
import { scaleIn } from "@/lib/motion/variants";

const SEVERITY_STYLES: Record<string, string> = {
  critical: "bg-error-bg text-error",
  high: "bg-warning-bg text-warning",
  medium: "bg-gray-100 text-gray-700",
  low: "bg-gray-50 text-gray-500",
};

interface SeverityBadgeProps {
  severity: FindingSeverity | string;
}

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  const normalized = severity.toLowerCase();
  const style = SEVERITY_STYLES[normalized] ?? SEVERITY_STYLES.medium;
  const motionEnabled = useMotionEnabled();

  const className = `inline-flex h-7 items-center rounded-pill px-3 text-caption font-medium capitalize ${style}`;

  if (!motionEnabled) {
    return <span className={className}>{severity}</span>;
  }

  return (
    <motion.span
      variants={scaleIn}
      initial="hidden"
      animate="visible"
      className={className}
    >
      {severity}
    </motion.span>
  );
}
