"use client";

import { motion } from "framer-motion";
import { forwardRef, type HTMLAttributes } from "react";

import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";
import { cardHover } from "@/lib/motion/variants";
import { cn } from "@/lib/utils";

type GlassCardProps = HTMLAttributes<HTMLDivElement> & {
  elevated?: boolean;
  subtle?: boolean;
  interactive?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
};

const paddingMap = {
  none: "",
  sm: "p-6",
  md: "p-8",
  lg: "p-10",
};

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  (
    {
      className,
      elevated = false,
      subtle = false,
      interactive = false,
      padding = "md",
      children,
      ...props
    },
    ref,
  ) => {
    const motionEnabled = useMotionEnabled();

    const surfaceClass = elevated ? "glass-elevated" : subtle ? "glass-subtle" : "glass";
    const classes = cn(
      "rounded-card",
      surfaceClass,
      interactive && "transition-all duration-normal hover:-translate-y-1 hover:shadow-elevation-2",
      paddingMap[padding],
      className,
    );

    if (interactive && motionEnabled) {
      return (
        <motion.div
          ref={ref}
          variants={cardHover}
          initial="rest"
          whileHover="hover"
          className={classes}
        >
          {children}
        </motion.div>
      );
    }

    return (
      <div ref={ref} className={classes} {...props}>
        {children}
      </div>
    );
  },
);

GlassCard.displayName = "GlassCard";
