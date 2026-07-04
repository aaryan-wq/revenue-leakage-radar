"use client";

import { useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";

/**
 * Returns true only after client mount and when the user has not requested reduced motion.
 * Use this to gate Framer Motion initial/animate props and avoid SSR hydration mismatches.
 */
export function useMotionEnabled(): boolean {
  const prefersReduced = useReducedMotion();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return mounted && !prefersReduced;
}
