"use client";

import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Check, Copy, Linkedin, Mail, Share2, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/hairline-card";
import { captureEvent } from "@/lib/analytics/client";
import { createShareLink } from "@/lib/estimator/api";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";
import {
  canNativeShare,
  openShareChannel,
  shareNative,
  type ShareChannel,
} from "@/lib/share";
import { AnalyticsEvents, formatCurrency } from "@rlr/shared";

interface EstimatorShareModalProps {
  open: boolean;
  onClose: () => void;
  assessmentId: string;
  estimateHigh: number;
}

function XIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className={className} fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

const SOCIAL_CHANNELS: { id: ShareChannel; label: string; icon: ReactNode }[] = [
  { id: "linkedin", label: "LinkedIn", icon: <Linkedin className="h-5 w-5" strokeWidth={1.75} /> },
  { id: "x", label: "X", icon: <XIcon className="h-4 w-4" /> },
  { id: "email", label: "Email", icon: <Mail className="h-5 w-5" strokeWidth={1.75} /> },
];

export function EstimatorShareModal({
  open,
  onClose,
  assessmentId,
  estimateHigh,
}: EstimatorShareModalProps) {
  const motionEnabled = useMotionEnabled();
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [nativeAvailable, setNativeAvailable] = useState(false);

  const loadShareUrl = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const share = await createShareLink(assessmentId);
      setShareUrl(`${window.location.origin}${share.share_path}`);
    } catch {
      setError("Unable to create share link. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [assessmentId]);

  useEffect(() => {
    setNativeAvailable(canNativeShare());
  }, []);

  useEffect(() => {
    if (!open) {
      setCopied(false);
      return;
    }
    void loadShareUrl();
  }, [open, loadShareUrl]);

  useEffect(() => {
    if (!open) return;

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

  const handleCopy = async () => {
    if (!shareUrl) return;
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      captureEvent(AnalyticsEvents.RESULT_SHARED, {
        assessment_id: assessmentId,
        channel: "copy",
      });
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Unable to copy link.");
    }
  };

  const handleChannel = (channel: ShareChannel) => {
    if (!shareUrl) return;
    openShareChannel(channel, shareUrl, estimateHigh);
    captureEvent(AnalyticsEvents.RESULT_SHARED, {
      assessment_id: assessmentId,
      channel,
    });
  };

  const handleNativeShare = async () => {
    if (!shareUrl) return;
    const shared = await shareNative(shareUrl, estimateHigh);
    if (shared) {
      captureEvent(AnalyticsEvents.RESULT_SHARED, {
        assessment_id: assessmentId,
        channel: "native",
      });
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[60] flex items-end justify-center p-4 sm:items-center sm:p-6">
          <motion.button
            type="button"
            aria-label="Close share dialog"
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
            aria-labelledby="share-modal-title"
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

              <p className="text-overline text-muted-foreground">Share estimate</p>
              <h2 id="share-modal-title" className="mt-3 pr-10 text-h3 text-foreground">
                Share with your team
              </h2>
              <p className="mt-2 text-small text-muted-foreground">
                Send a read-only link showing ~{formatCurrency(estimateHigh)}/year in estimated
                recoverable revenue.
              </p>

              <div className="mt-8 space-y-6">
                {loading ? (
                  <div className="flex items-center gap-3 rounded-xl border border-border/50 bg-surface-glass-subtle px-4 py-3">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-muted-foreground/30 border-t-foreground" />
                    <p className="text-small text-muted-foreground">Creating share link…</p>
                  </div>
                ) : error ? (
                  <div className="space-y-3">
                    <p className="text-small text-destructive">{error}</p>
                    <Button variant="secondary" onClick={() => void loadShareUrl()} className="min-h-[44px]">
                      Try again
                    </Button>
                  </div>
                ) : shareUrl ? (
                  <>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        readOnly
                        value={shareUrl}
                        aria-label="Share link"
                        className="min-h-[44px] flex-1 truncate rounded-xl border border-border/50 bg-surface-glass-subtle px-4 py-3 text-small text-foreground focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/20"
                        onFocus={(e) => e.target.select()}
                      />
                      <Button
                        variant="secondary"
                        onClick={() => void handleCopy()}
                        className="min-h-[44px] shrink-0 px-4"
                        aria-label={copied ? "Copied" : "Copy link"}
                      >
                        {copied ? (
                          <Check className="h-4 w-4 text-success" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                        <span className="ml-2 hidden sm:inline">{copied ? "Copied" : "Copy"}</span>
                      </Button>
                    </div>

                    <div className="space-y-4">
                      <p className="text-caption text-muted-foreground">Share via</p>
                      <div className="flex flex-wrap gap-3">
                        {SOCIAL_CHANNELS.map((channel) => (
                          <button
                            key={channel.id}
                            type="button"
                            onClick={() => handleChannel(channel.id)}
                            className="focus-ring flex min-h-[44px] min-w-[44px] flex-col items-center justify-center gap-1 rounded-xl border border-border/50 bg-surface-glass-subtle px-5 py-3 transition-colors hover:bg-secondary"
                          >
                            {channel.icon}
                            <span className="text-caption text-muted-foreground">{channel.label}</span>
                          </button>
                        ))}
                        {nativeAvailable ? (
                          <button
                            type="button"
                            onClick={() => void handleNativeShare()}
                            className="focus-ring flex min-h-[44px] min-w-[44px] flex-col items-center justify-center gap-1 rounded-xl border border-border/50 bg-surface-glass-subtle px-5 py-3 transition-colors hover:bg-secondary"
                          >
                            <Share2 className="h-5 w-5" strokeWidth={1.75} />
                            <span className="text-caption text-muted-foreground">More</span>
                          </button>
                        ) : null}
                      </div>
                    </div>
                  </>
                ) : null}
              </div>
            </HairlineCard>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
