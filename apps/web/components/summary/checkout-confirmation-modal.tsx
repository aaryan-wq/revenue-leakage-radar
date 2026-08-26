"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, X } from "lucide-react";

import {
  CONFIRMED_RECOVERY_DEFINITION,
  SUCCESS_FEE_RATE_LABEL,
  VERIFICATION_REPORT_BASE_FEE,
  computeCheckoutTotal,
} from "@/lib/pricing-content";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/hairline-card";
import { formatCurrency, parseUsdAmount } from "@rlr/shared";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";

interface CheckoutConfirmationModalProps {
  open: boolean;
  onClose: () => void;
  identifiedRecoverableArr: string;
  onConfirm: (confirmedRecoveryUsd: number) => Promise<void>;
  isSubmitting?: boolean;
  error?: string | null;
}

function formatUsdInput(value: number): string {
  if (!Number.isFinite(value)) return "0";
  return value.toFixed(2);
}

export function CheckoutConfirmationModal({
  open,
  onClose,
  identifiedRecoverableArr,
  onConfirm,
  isSubmitting = false,
  error = null,
}: CheckoutConfirmationModalProps) {
  const motionEnabled = useMotionEnabled();
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const identifiedUsd = parseUsdAmount(identifiedRecoverableArr);
  const [confirmedInput, setConfirmedInput] = useState(formatUsdInput(identifiedUsd));
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setConfirmedInput(formatUsdInput(identifiedUsd));
    setValidationError(null);
  }, [open, identifiedUsd]);

  useEffect(() => {
    if (!open) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !isSubmitting) onClose();
    }

    window.addEventListener("keydown", handleKeyDown);
    closeButtonRef.current?.focus();

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onClose, isSubmitting]);

  const confirmedUsd = parseUsdAmount(confirmedInput);
  const breakdown = useMemo(() => computeCheckoutTotal(confirmedUsd), [confirmedUsd]);

  const handleConfirm = async () => {
    if (confirmedUsd > identifiedUsd) {
      setValidationError("Confirmed recovery cannot exceed the amount identified in your free audit.");
      return;
    }
    setValidationError(null);
    await onConfirm(confirmedUsd);
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[60] flex items-end justify-center p-4 sm:items-center sm:p-6">
          <motion.button
            type="button"
            aria-label="Close checkout confirmation dialog"
            className="absolute inset-0 bg-background/70 backdrop-blur-sm"
            initial={motionEnabled ? { opacity: 0 } : false}
            animate={{ opacity: 1 }}
            exit={motionEnabled ? { opacity: 0 } : { opacity: 0 }}
            transition={{ duration: motionEnabled ? 0.2 : 0.15 }}
            onClick={() => {
              if (!isSubmitting) onClose();
            }}
          />

          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="checkout-modal-title"
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
                disabled={isSubmitting}
                className="focus-ring absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-full text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground disabled:opacity-50"
                aria-label="Close"
              >
                <X className="h-5 w-5" strokeWidth={1.75} />
              </button>

              <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
                Checkout
              </p>
              <h2
                id="checkout-modal-title"
                className="mt-3 pr-10 font-heading text-2xl tracking-tight text-balance"
              >
                Confirm recovery before payment
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {CONFIRMED_RECOVERY_DEFINITION}
              </p>

              <div className="mt-8 space-y-6">
                <div>
                  <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                    Identified recoverable ARR
                  </p>
                  <p className="mt-2 font-heading text-2xl tracking-tight tnum">
                    {formatCurrency(identifiedRecoverableArr)}
                  </p>
                </div>

                <div>
                  <label htmlFor="confirmed-recovery" className="text-sm font-medium text-foreground">
                    Confirmed recovery
                  </label>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Adjust if you expect to recover less than the full identified amount.
                  </p>
                  <div className="relative mt-3">
                    <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
                      $
                    </span>
                    <input
                      id="confirmed-recovery"
                      type="text"
                      inputMode="decimal"
                      value={confirmedInput}
                      onChange={(event) => setConfirmedInput(event.target.value)}
                      className="focus-ring w-full rounded-xl border border-line bg-surface-glass-subtle px-4 py-3 pl-8 text-sm tnum text-foreground"
                      aria-describedby="confirmed-recovery-help"
                    />
                  </div>
                  <p id="confirmed-recovery-help" className="mt-2 text-xs text-muted-foreground">
                    Maximum: {formatCurrency(identifiedRecoverableArr)}
                  </p>
                  {validationError && (
                    <p className="mt-2 text-sm text-leak">{validationError}</p>
                  )}
                </div>

                <div className="rounded-xl border border-line bg-surface-glass-subtle p-5">
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center justify-between gap-4">
                      <span className="text-muted-foreground">Base audit fee</span>
                      <span className="tnum text-foreground">{VERIFICATION_REPORT_BASE_FEE}</span>
                    </div>
                    <div className="flex items-center justify-between gap-4">
                      <span className="text-muted-foreground">
                        Success fee ({SUCCESS_FEE_RATE_LABEL})
                      </span>
                      <span className="tnum text-foreground">
                        {formatCurrency(breakdown.successFeeUsd)}
                      </span>
                    </div>
                    <div className="border-t border-line pt-3">
                      <div className="flex items-center justify-between gap-4">
                        <span className="font-medium text-foreground">Total due today</span>
                        <span className="font-heading text-xl tracking-tight tnum">
                          {formatCurrency(breakdown.totalUsd)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {(error || validationError) && error && (
                  <p className="text-sm text-leak">{error}</p>
                )}

                <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
                  <Button
                    variant="secondary"
                    size="lg"
                    onClick={onClose}
                    disabled={isSubmitting}
                    className="sm:min-w-32"
                  >
                    Cancel
                  </Button>
                  <Button
                    size="lg"
                    onClick={() => void handleConfirm()}
                    disabled={isSubmitting}
                    className="sm:min-w-40"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" strokeWidth={1.75} />
                        Processing…
                      </>
                    ) : (
                      "Continue to payment"
                    )}
                  </Button>
                </div>
              </div>
            </HairlineCard>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
