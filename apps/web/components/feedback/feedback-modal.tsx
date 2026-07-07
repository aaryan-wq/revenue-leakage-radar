"use client";

import { useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { AnalyticsEvents } from "@rlr/shared";

import { FeedbackForm } from "@/components/feedback/feedback-form";
import { HairlineCard } from "@/components/ui/hairline-card";
import { captureEvent } from "@/lib/analytics/client";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";

interface FeedbackModalProps {
  open: boolean;
  onClose: () => void;
}

export function FeedbackModal({ open, onClose }: FeedbackModalProps) {
  const motionEnabled = useMotionEnabled();
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;

    captureEvent(AnalyticsEvents.FEEDBACK_FORM_OPENED, { source: "modal" });

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }

    window.addEventListener("keydown", handleKeyDown);
    closeButtonRef.current?.focus();

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[60] flex items-end justify-center p-4 sm:items-center sm:p-6">
          <motion.button
            type="button"
            aria-label="Close feedback dialog"
            className="absolute inset-0 bg-background/70 backdrop-blur-sm"
            initial={motionEnabled ? { opacity: 0 } : false}
            animate={{ opacity: 1 }}
            exit={motionEnabled ? { opacity: 0 } : { opacity: 0 }}
            transition={{ duration: motionEnabled ? 0.2 : 0.15 }}
            onClick={onClose}
          />

          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="feedback-modal-title"
            className="relative z-10 w-full max-w-lg"
            initial={motionEnabled ? { opacity: 0, y: 24, scale: 0.98 } : false}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={motionEnabled ? { opacity: 0, y: 16, scale: 0.98 } : { opacity: 0 }}
            transition={{ duration: motionEnabled ? 0.25 : 0.15, ease: "easeOut" }}
          >
            <HairlineCard padding="lg" elevated className="relative">
              <button
                ref={closeButtonRef}
                type="button"
                onClick={onClose}
                className="focus-ring absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-full text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                aria-label="Close"
              >
                <X className="h-5 w-5" strokeWidth={1.75} />
              </button>

              <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
                Feedback
              </p>
              <h2
                id="feedback-modal-title"
                className="mt-3 pr-10 font-heading text-2xl tracking-tight text-balance"
              >
                We want to hear from you
              </h2>
              <p className="mt-2 text-[0.92rem] leading-relaxed text-muted-foreground">
                Every message goes directly to our team and helps shape Paevo.
              </p>

              <FeedbackForm source="modal" onSuccess={onClose} className="mt-8" />
            </HairlineCard>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
