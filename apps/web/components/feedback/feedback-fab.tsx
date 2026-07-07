"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { MessageSquarePlus } from "lucide-react";
import { AnalyticsEvents } from "@rlr/shared";

import { FeedbackModal } from "@/components/feedback/feedback-modal";
import { captureEvent } from "@/lib/analytics/client";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";
import { cn } from "@/lib/utils";

const SEEN_KEY = "rlr_feedback_seen";

export function FeedbackFab() {
  const [open, setOpen] = useState(false);
  const [showPulse, setShowPulse] = useState(false);
  const motionEnabled = useMotionEnabled();

  useEffect(() => {
    if (typeof window === "undefined") return;
    setShowPulse(!localStorage.getItem(SEEN_KEY));
  }, []);

  function handleOpen() {
    captureEvent(AnalyticsEvents.FEEDBACK_FAB_CLICKED);
    if (typeof window !== "undefined") {
      localStorage.setItem(SEEN_KEY, "1");
    }
    setShowPulse(false);
    setOpen(true);
  }

  return (
    <>
      <div className="fixed bottom-6 right-6 z-50">
        {showPulse && motionEnabled && (
          <motion.span
            aria-hidden="true"
            className="absolute inset-0 rounded-full bg-primary/20"
            animate={{ scale: [1, 1.35, 1], opacity: [0.6, 0, 0.6] }}
            transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
          />
        )}
        <button
          type="button"
          onClick={handleOpen}
          className={cn(
            "focus-ring relative inline-flex h-12 items-center gap-2 rounded-full border border-line bg-card px-4 text-[0.82rem] font-medium text-foreground shadow-[0_12px_40px_-12px_rgba(0,0,0,0.35)] transition-transform hover:-translate-y-0.5 sm:h-14 sm:px-5 sm:text-[0.88rem]",
          )}
          aria-label="Open feedback form"
        >
          <MessageSquarePlus className="h-5 w-5 shrink-0" strokeWidth={1.75} />
          <span className="hidden sm:inline">Feedback</span>
        </button>
      </div>

      <FeedbackModal open={open} onClose={() => setOpen(false)} />
    </>
  );
}
