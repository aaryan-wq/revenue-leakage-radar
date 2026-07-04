"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

import { glide } from "@/components/motion";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";

const STAGES = [
  { label: "Upload", detail: "Receiving billing and CRM exports" },
  { label: "Parse", detail: "Reading CSV structure and encoding" },
  { label: "Normalize", detail: "Converting to canonical data model" },
  { label: "Validation", detail: "Checking schema, relationships, and duplicates" },
  { label: "Verification Checks", detail: "Running deterministic leakage rules" },
  { label: "Revenue Estimation", detail: "Quantifying recoverable annual revenue" },
  { label: "Report Generation", detail: "Ranking findings by confidence" },
] as const;

/** Minimum time to play through the full visual cycle once. */
const MIN_CYCLE_MS = 18_000;
const TICK_MS = 80;

interface AnimatedScanPipelineProps {
  rulesCompleted?: number;
  rulesTotal?: number;
  onCycleComplete?: () => void;
}

export function AnimatedScanPipeline({
  rulesCompleted = 0,
  rulesTotal = 0,
  onCycleComplete,
}: AnimatedScanPipelineProps) {
  const motionEnabled = useMotionEnabled();
  const [elapsedMs, setElapsedMs] = useState(0);
  const cycleCompleteRef = useRef(false);

  useEffect(() => {
    const startedAt = Date.now();
    const timer = window.setInterval(() => {
      const next = Date.now() - startedAt;
      setElapsedMs(next);
      if (next >= MIN_CYCLE_MS && !cycleCompleteRef.current) {
        cycleCompleteRef.current = true;
        onCycleComplete?.();
      }
    }, TICK_MS);
    return () => window.clearInterval(timer);
  }, [onCycleComplete]);

  const rawProgress = Math.min(elapsedMs / MIN_CYCLE_MS, 1);
  const stageCount = STAGES.length;
  const phaseFloat = rawProgress * (stageCount - 1);
  const phase = Math.min(Math.floor(phaseFloat), stageCount - 1);
  const phaseProgress = phaseFloat - phase;
  const displayProgress = Math.min((phase + phaseProgress * 0.85 + 0.05) / stageCount, 0.99);
  const progressPercent = rawProgress >= 1 ? 100 : Math.round(displayProgress * 100);
  const currentStage = STAGES[phase] ?? STAGES[0];
  const ringCircumference = 2 * Math.PI * 88;
  const isCycleDone = elapsedMs >= MIN_CYCLE_MS;

  const verificationDetail =
    rulesTotal > 0 && phase >= 4
      ? `Running verification rules (${rulesCompleted} of ${rulesTotal})`
      : currentStage.detail;

  return (
    <div className="flex flex-col items-center text-center">
      <div className="relative mb-16 h-56 w-56">
        <svg viewBox="0 0 200 200" className="h-full w-full -rotate-90">
          <circle cx="100" cy="100" r="88" fill="none" stroke="var(--line)" strokeWidth="1" />
          <motion.circle
            cx="100"
            cy="100"
            r="88"
            fill="none"
            stroke="var(--primary)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeDasharray={ringCircumference}
            animate={{
              strokeDashoffset: ringCircumference * (1 - displayProgress),
            }}
            transition={{ ease: "linear", duration: motionEnabled ? 0.15 : 0 }}
          />
        </svg>

        {motionEnabled &&
          !isCycleDone &&
          [64, 44, 26].map((radius, index) => (
            <motion.span
              key={radius}
              className="absolute left-1/2 top-1/2 rounded-full border border-primary/20"
              style={{
                width: radius * 2,
                height: radius * 2,
                marginLeft: -radius,
                marginTop: -radius,
              }}
              animate={{ scale: [1, 1.1, 1], opacity: [0.45, 0.15, 0.45] }}
              transition={{
                duration: 2.2,
                repeat: Infinity,
                delay: index * 0.25,
                ease: "easeInOut",
              }}
            />
          ))}

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-heading text-4xl tracking-tight tnum">{progressPercent}%</span>
          <span className="mt-1 text-[0.7rem] uppercase tracking-[0.18em] text-muted-foreground">
            {isCycleDone ? "Finalizing" : "Analyzing"}
          </span>
        </div>
      </div>

      <div className="h-16">
        {motionEnabled ? (
          <AnimatePresence mode="wait">
            <motion.div
              key={phase}
              initial={{ opacity: 0, y: 12, filter: "blur(6px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -12, filter: "blur(6px)" }}
              transition={{ duration: 0.5, ease: glide }}
            >
              <p className="font-heading text-2xl tracking-tight">{currentStage.label}</p>
              <p className="mt-2 text-sm text-muted-foreground">{verificationDetail}</p>
            </motion.div>
          </AnimatePresence>
        ) : (
          <div>
            <p className="font-heading text-2xl tracking-tight">{currentStage.label}</p>
            <p className="mt-2 text-sm text-muted-foreground">{verificationDetail}</p>
          </div>
        )}
      </div>

      <div className="mt-12 flex items-center gap-2.5">
        {STAGES.map((stage, index) => (
          <motion.span
            key={stage.label}
            className="h-1 rounded-full"
            animate={{
              width: index === phase ? 36 : 8,
              backgroundColor:
                index < phase || (index === phase && phaseProgress > 0.3)
                  ? "var(--primary)"
                  : index === phase
                    ? "color-mix(in oklch, var(--primary) 50%, var(--line))"
                    : "var(--line)",
            }}
            transition={{ type: "spring", stiffness: 260, damping: 26 }}
          />
        ))}
      </div>

      <p className="mt-8 text-sm text-muted-foreground">
        {isCycleDone ? "Wrapping up results…" : "~2–4 min remaining"}
      </p>

      <p className="mt-4 max-w-sm text-sm leading-relaxed text-muted-foreground">
        This usually takes under a minute. We&apos;re being thorough so the findings are ones you
        can stand behind.
      </p>
    </div>
  );
}
