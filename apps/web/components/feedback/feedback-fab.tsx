"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { MessageSquarePlus } from "lucide-react";
import { AnalyticsEvents } from "@rlr/shared";

import { FeedbackModal } from "@/components/feedback/feedback-modal";
import { captureEvent } from "@/lib/analytics/client";
import { localStorageGetItem, localStorageSetItem } from "@/lib/browser-storage";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";
import { cn } from "@/lib/utils";

const SEEN_KEY = "rlr_feedback_seen";

export function FeedbackFab() {
  const [open, setOpen] = useState(false);
  const [showPulse, setShowPulse] = useState(false);
  const motionEnabled = useMotionEnabled();

  useEffect(() => {
    if (typeof window === "undefined") return;
    setShowPulse(!localStorageGetItem(SEEN_KEY));
  }, []);

  function handleOpen() {
    captureEvent(AnalyticsEvents.FEEDBACK_FAB_CLICKED);
    if (typeof window !== "undefined") {
      localStorageSetItem(SEEN_KEY, "1");
    }
    setShowPulse(false);
    setOpen(true);
  }

  return (
    <>
      <div className="fixed bottom-4 right-4 z-50 sm:bottom-6 sm:right-6">
        <div className="relative">
          {showPulse && motionEnabled && (
            <motion.span
              aria-hidden="true"
              className="pointer-events-none absolute inset-0 rounded-full bg-primary/20"
              animate={{ scale: [1, 1.25, 1], opacity: [0.5, 0, 0.5] }}
              transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
            />
          )}
          <button
            type="button"
            onClick={handleOpen}
            className={cn(
              "focus-ring relative inline-flex h-11 w-11 items-center justify-center rounded-full border border-line bg-card text-foreground shadow-[0_8px_28px_-12px_rgba(0,0,0,0.35)] transition-transform hover:-translate-y-0.5",
              "sm:h-12 sm:w-auto sm:gap-2 sm:px-4 sm:text-[0.82rem] sm:font-medium",
              "md:h-14 md:px-5 md:text-[0.88rem]",
            )}
            aria-label="Open feedback form"
          >
            <MessageSquarePlus className="h-4 w-4 shrink-0 sm:h-5 sm:w-5" strokeWidth={1.75} />
            <span className="hidden sm:inline">Feedback</span>
          </button>
        </div>
      </div>

      <FeedbackModal open={open} onClose={() => setOpen(false)} />
    </>
  );
}
