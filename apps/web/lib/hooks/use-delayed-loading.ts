"use client";

import { useEffect, useRef, useState } from "react";

/** Wait this long before showing loading UI (avoids flash on fast requests). */
export const LOADING_DELAY_MS = 180;

/** Once visible, keep loading UI at least this long so exit animation reads cleanly. */
export const LOADING_MIN_VISIBLE_MS = 220;

/**
 * Returns true only after `isLoading` has been true for at least `delayMs`.
 * Resets immediately when loading finishes before the delay (never flashes).
 * When loading UI was shown, holds true briefly so exit animations can play.
 */
export function useDelayedLoading(
  isLoading: boolean,
  delayMs = LOADING_DELAY_MS,
  minVisibleMs = LOADING_MIN_VISIBLE_MS,
): boolean {
  const [visible, setVisible] = useState(false);
  const isLoadingRef = useRef(isLoading);
  const shownAtRef = useRef(0);
  const delayTimerRef = useRef<number | undefined>(undefined);
  const hideTimerRef = useRef<number | undefined>(undefined);

  isLoadingRef.current = isLoading;

  useEffect(() => {
    window.clearTimeout(delayTimerRef.current);
    window.clearTimeout(hideTimerRef.current);

    if (isLoading) {
      setVisible(false);
      delayTimerRef.current = window.setTimeout(() => {
        if (isLoadingRef.current) {
          shownAtRef.current = Date.now();
          setVisible(true);
        }
      }, delayMs);
      return () => window.clearTimeout(delayTimerRef.current);
    }

    setVisible((currentlyVisible) => {
      if (!currentlyVisible) return false;

      const elapsed = Date.now() - shownAtRef.current;
      const remaining = Math.max(0, minVisibleMs - elapsed);

      hideTimerRef.current = window.setTimeout(() => {
        setVisible(false);
      }, remaining);

      return true;
    });

    return () => window.clearTimeout(hideTimerRef.current);
  }, [isLoading, delayMs, minVisibleMs]);

  return visible;
}

/**
 * For components that mount only while loading (early-return pattern).
 * Delays appearance; unmount is handled by the parent when loading completes.
 */
export function useDelayedMount(delayMs = LOADING_DELAY_MS): boolean {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => setVisible(true), delayMs);
    return () => window.clearTimeout(timer);
  }, [delayMs]);

  return visible;
}
