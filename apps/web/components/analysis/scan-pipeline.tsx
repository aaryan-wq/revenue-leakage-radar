"use client";

import { AnimatePresence, motion } from "framer-motion";

import { glide } from "@/components/motion";
import { useSmoothProgress } from "@/lib/hooks/use-smooth-progress";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";
import type { AuditStatus } from "@rlr/shared";

type StageStatus = "complete" | "active" | "pending";

interface PipelineStage {
  label: string;
  detail: string;
  status: StageStatus;
}

const STAGE_DETAILS: Record<string, string> = {
  Upload: "Receiving billing and CRM exports",
  Parse: "Reading CSV structure and encoding",
  Normalize: "Converting to canonical data model",
  Validation: "Checking schema, relationships, and duplicates",
  "Verification Checks": "Running deterministic leakage rules",
  "Revenue Estimation": "Quantifying recoverable annual revenue",
  "Report Generation": "Ranking findings by confidence",
};

const STAGE_LABELS = [
  "Upload",
  "Parse",
  "Normalize",
  "Validation",
  "Verification Checks",
  "Revenue Estimation",
  "Report Generation",
] as const;

function buildStages(status: AuditStatus, progress: number): PipelineStage[] {
  const stageCount = STAGE_LABELS.length;
  const activeIndex = Math.min(stageCount - 1, Math.floor(progress * stageCount));

  return STAGE_LABELS.map((label, index) => {
    let stageStatus: StageStatus = "pending";
    if (index < activeIndex) {
      stageStatus = "complete";
    } else if (index === activeIndex) {
      stageStatus = status === "completed" && progress >= 1 ? "complete" : "active";
    }

    return {
      label,
      detail: STAGE_DETAILS[label] ?? "",
      status: stageStatus,
    };
  });
}

function estimateRemainingMinutes(progress: number): string {
  if (progress >= 0.95) return "Almost done";
  if (progress >= 0.7) return "~1–2 min remaining";
  return "~2–4 min remaining";
}

interface ScanPipelineProps {
  status: AuditStatus;
  rulesCompleted?: number;
  rulesTotal?: number;
  /** Backend scan finished — progress animation will complete to 100%. */
  backendComplete?: boolean;
  /** Show a static 100% ring (post-scan results view). */
  instantComplete?: boolean;
  onVisualComplete?: () => void;
}

export function ScanPipeline({
  status,
  rulesCompleted = 0,
  rulesTotal = 0,
  backendComplete = false,
  instantComplete = false,
  onVisualComplete,
}: ScanPipelineProps) {
  const motionEnabled = useMotionEnabled();
  const isBackendDone = instantComplete || backendComplete || status === "completed";
  const progress = useSmoothProgress({
    isComplete: isBackendDone,
    minDurationMs: 4_000,
    onReached100: onVisualComplete,
    disabled: instantComplete,
  });

  const stages = buildStages(status, progress);
  const phase = Math.min(
    stages.length - 1,
    stages.findIndex((stage) => stage.status === "active"),
  );
  const currentStage = stages[phase >= 0 ? phase : stages.length - 1];
  const progressPercent = Math.min(100, Math.round(progress * 100));
  const isComplete = progressPercent >= 100;
  const centerLabel = isComplete ? "Complete" : progress >= 0.9 ? "Finalizing" : "Analyzing";
  const ringCircumference = 2 * Math.PI * 88;

  const verificationDetail =
    rulesTotal > 0 && phase >= 4
      ? `Running verification rules (${rulesCompleted} of ${rulesTotal})`
      : currentStage?.detail;

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
              strokeDashoffset: ringCircumference * (1 - progress),
            }}
            transition={{ ease: "linear", duration: motionEnabled ? 0.12 : 0 }}
          />
        </svg>

        {motionEnabled &&
          !isComplete &&
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
              animate={{ scale: [1, 1.08, 1], opacity: [0.5, 0.2, 0.5] }}
              transition={{
                duration: 2.6,
                repeat: Infinity,
                delay: index * 0.3,
                ease: "easeInOut",
              }}
            />
          ))}

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-heading text-4xl tracking-tight tnum">{progressPercent}%</span>
          <span className="mt-1 text-[0.7rem] uppercase tracking-[0.18em] text-muted-foreground">
            {centerLabel}
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
              transition={{ duration: 0.6, ease: glide }}
            >
              <p className="font-heading text-2xl tracking-tight">{currentStage?.label}</p>
              <p className="mt-2 text-sm text-muted-foreground">{verificationDetail}</p>
            </motion.div>
          </AnimatePresence>
        ) : (
          <div>
            <p className="font-heading text-2xl tracking-tight">{currentStage?.label}</p>
            <p className="mt-2 text-sm text-muted-foreground">{verificationDetail}</p>
          </div>
        )}
      </div>

      <div className="mt-12 flex items-center gap-2.5">
        {stages.map((stage, index) => (
          <motion.span
            key={stage.label}
            className="h-1 rounded-full"
            animate={{
              width: index === phase ? 36 : 8,
              backgroundColor: index <= phase ? "var(--primary)" : "var(--line)",
            }}
            transition={{ type: "spring", stiffness: 260, damping: 26 }}
          />
        ))}
      </div>

      {!isComplete && (
        <p className="mt-8 text-sm text-muted-foreground">
          {estimateRemainingMinutes(progress)}
        </p>
      )}

      {status === "scanning" && rulesTotal > 0 && (
        <p className="mt-3 text-sm text-muted-foreground tnum">
          Running verification rules ({rulesCompleted} of {rulesTotal})
        </p>
      )}

      {!isComplete && (
        <p className="mt-8 max-w-sm text-sm leading-relaxed text-muted-foreground">
          This usually takes under a minute. We&apos;re being thorough so the findings are ones you
          can stand behind.
        </p>
      )}
    </div>
  );
}
