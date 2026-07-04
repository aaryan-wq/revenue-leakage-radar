"use client";

import { motion } from "framer-motion";

import { pageTransition, reducedMotionFade } from "@/lib/motion/variants";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";

export function PageTransition({ children }: { children: React.ReactNode }) {
  const motionEnabled = useMotionEnabled();
  const variants = motionEnabled ? pageTransition : reducedMotionFade;

  return (
    <motion.div
      initial={motionEnabled ? "initial" : false}
      animate={motionEnabled ? "animate" : false}
      exit={motionEnabled ? "exit" : undefined}
      variants={variants}
    >
      {children}
    </motion.div>
  );
}
