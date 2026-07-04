"use client";

import { motion } from "framer-motion";

import type { FindingSeverity } from "@rlr/shared";

import {
  getSeverityLabel,
  getSeverityTextClass,
} from "@/components/findings/severity-utils";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";
import { scaleIn } from "@/lib/motion/variants";

interface SeverityBadgeProps {
  severity: FindingSeverity | string;
}

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  const motionEnabled = useMotionEnabled();
  const className = `text-[0.72rem] uppercase tracking-[0.14em] ${getSeverityTextClass(severity)}`;

  if (!motionEnabled) {
    return <span className={className}>{getSeverityLabel(severity)}</span>;
  }

  return (
    <motion.span
      variants={scaleIn}
      initial="hidden"
      animate="visible"
      className={className}
    >
      {getSeverityLabel(severity)}
    </motion.span>
  );
}
