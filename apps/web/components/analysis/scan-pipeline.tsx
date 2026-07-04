"use client";

import { AnimatePresence, motion } from "framer-motion";

import { glide } from "@/components/motion";
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

function buildStages(status: AuditStatus): PipelineStage[] {
  const preScanComplete =
    status !== "ready_for_scan" && status !== "created" && status !== "uploading";
  const upload: StageStatus = preScanComplete
    ? "complete"
    : status === "uploading"
      ? "active"
      : "pending";
  const parse: StageStatus = preScanComplete ? "complete" : "pending";
  const normalize: StageStatus = preScanComplete ? "complete" : "pending";
  const validation: StageStatus = preScanComplete ? "complete" : "pending";

  const verification: StageStatus =
    status === "scanning" || status === "ready_for_scan"
      ? "active"
      : status === "completed" || status === "generating_report"
        ? "complete"
        : "pending";
  const estimation: StageStatus =
    status === "generating_report" ? "active" : status === "completed" ? "complete" : "pending";
  const report: StageStatus = status === "completed" ? "complete" : "pending";

  const labels = [
    "Upload",
    "Parse",
    "Normalize",
    "Validation",
    "Verification Checks",
    "Revenue Estimation",
    "Report Generation",
  ] as const;

  const statuses = [upload, parse, normalize, validation, verification, estimation, report];

  return labels.map((label, index) => ({
    label,
    detail: STAGE_DETAILS[label] ?? "",
    status: statuses[index] ?? "pending",
  }));
}

function estimateRemainingMinutes(rulesTotal: number, status: AuditStatus): string {
  if (status === "generating_report") return "~1 min remaining";
  if (status === "scanning") {
    if (rulesTotal >= 20) return "~3–5 min remaining";
    return "~2–3 min remaining";
  }
  return "~2–5 min remaining";
}

function getPhaseIndex(stages: PipelineStage[]): number {
  const activeIndex = stages.findIndex((stage) => stage.status === "active");
  if (activeIndex >= 0) return activeIndex;
  const completedCount = stages.filter((stage) => stage.status === "complete").length;
  return Math.min(completedCount, stages.length - 1);
}

function getProgress(
  stages: PipelineStage[],
  status: AuditStatus,
  rulesCompleted: number,
  rulesTotal: number,
): number {
  if (status === "completed") return 1;

  const completedCount = stages.filter((stage) => stage.status === "complete").length;
  const activeIndex = stages.findIndex((stage) => stage.status === "active");

  if (status === "scanning" && rulesTotal > 0) {
    const verificationProgress = Math.min(rulesCompleted / rulesTotal, 1);
    return Math.min((4 + verificationProgress * 0.9) / stages.length, 0.96);
  }

  if (activeIndex >= 0) {
    return Math.min((completedCount + 0.6) / stages.length, 0.96);
  }

  if (status === "ready_for_scan") {
    return 4 / stages.length;
  }

  return completedCount / stages.length;
}

interface ScanPipelineProps {
  status: AuditStatus;
  rulesCompleted?: number;
  rulesTotal?: number;
}

export function ScanPipeline({ status, rulesCompleted = 0, rulesTotal = 0 }: ScanPipelineProps) {
  const motionEnabled = useMotionEnabled();
  const stages = buildStages(status);
  const phase = getPhaseIndex(stages);
  const progress = getProgress(stages, status, rulesCompleted, rulesTotal);
  const currentStage = stages[phase];
  const isProcessing =
    status === "scanning" || status === "generating_report" || status === "ready_for_scan";
  const isComplete = status === "completed";
  const progressPercent = Math.round(progress * 100);
  const centerLabel = isComplete ? "Complete" : status === "generating_report" ? "Finalizing" : "Analyzing";
  const ringCircumference = 2 * Math.PI * 88;

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
            transition={{ ease: "linear", duration: motionEnabled ? 0.4 : 0 }}
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
              <p className="mt-2 text-sm text-muted-foreground">{currentStage?.detail}</p>
            </motion.div>
          </AnimatePresence>
        ) : (
          <div>
            <p className="font-heading text-2xl tracking-tight">{currentStage?.label}</p>
            <p className="mt-2 text-sm text-muted-foreground">{currentStage?.detail}</p>
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

      {isProcessing && (
        <p className="mt-8 text-sm text-muted-foreground">
          {estimateRemainingMinutes(rulesTotal, status)}
        </p>
      )}

      {status === "scanning" && rulesTotal > 0 && (
        <p className="mt-3 text-sm text-muted-foreground tnum">
          Running verification rules ({rulesCompleted} of {rulesTotal})
        </p>
      )}

      {isProcessing && (
        <p className="mt-8 max-w-sm text-sm leading-relaxed text-muted-foreground">
          This usually takes under a minute. We&apos;re being thorough so the findings are ones you
          can stand behind.
        </p>
      )}
    </div>
  );
}
