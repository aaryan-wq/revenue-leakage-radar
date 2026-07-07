"use client";

import { useEffect, useRef, useState } from "react";

interface UseSmoothProgressOptions {
  /** Backend work finished — progress will ease to 100%. */
  isComplete: boolean;
  /** Minimum ms before allowing 100% even when backend is already done. */
  minDurationMs?: number;
  /** Called once display progress reaches 100%. */
  onReached100?: () => void;
  /** Skip animation and pin at 100%. */
  disabled?: boolean;
}

/**
 * Time-based progress that always animates 0→100 smoothly.
 * Crawls near the end while waiting for backend; finishes when both are ready.
 */
export function useSmoothProgress({
  isComplete,
  minDurationMs = 4_000,
  onReached100,
  disabled = false,
}: UseSmoothProgressOptions): number {
  const [progress, setProgress] = useState(disabled ? 1 : 0);
  const startRef = useRef<number | null>(null);
  const reachedRef = useRef(false);
  const onReached100Ref = useRef(onReached100);
  onReached100Ref.current = onReached100;

  useEffect(() => {
    if (disabled) {
      setProgress(1);
      return;
    }
    startRef.current = performance.now();
    reachedRef.current = false;
    setProgress(0);
  }, [disabled]);

  useEffect(() => {
    if (disabled) return;

    let raf = 0;

    const tick = (now: number) => {
      const startedAt = startRef.current ?? now;
      const elapsed = now - startedAt;
      const minElapsed = elapsed >= minDurationMs;

      setProgress((prev) => {
        let next: number;

        if (isComplete && minElapsed) {
          next = prev + (1 - prev) * 0.12;
          if (next >= 0.999) {
            next = 1;
          }
        } else {
          const t = elapsed / 1000;
          const natural = 1 - Math.exp(-t / 10) * 0.28;
          const ceiling = isComplete ? 0.97 : 0.93;
          const target = Math.min(ceiling, natural);
          const delta = (target - prev) * 0.08;
          next = Math.max(prev, prev + Math.max(delta, 0.0008));
        }

        if (next >= 1 && !reachedRef.current) {
          reachedRef.current = true;
          onReached100Ref.current?.();
        }

        return next;
      });

      raf = requestAnimationFrame(tick);
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [disabled, isComplete, minDurationMs]);

  return progress;
}
