import { Check, Circle, Loader2 } from "lucide-react";

import type { AuditStatus } from "@rlr/shared";

type StageStatus = "complete" | "active" | "pending";

interface PipelineStage {
  label: string;
  status: StageStatus;
}

function stageIcon(status: StageStatus) {
  if (status === "complete") {
    return <Check className="h-5 w-5 text-success" strokeWidth={2} />;
  }
  if (status === "active") {
    return <Loader2 className="h-5 w-5 animate-spin text-blue" strokeWidth={1.75} />;
  }
  return <Circle className="h-5 w-5 text-gray-300" strokeWidth={1.75} />;
}

function buildStages(status: AuditStatus): PipelineStage[] {
  const verification: StageStatus =
    status === "scanning" ? "active" : status === "completed" || status === "generating_report" ? "complete" : "pending";
  const estimation: StageStatus =
    status === "generating_report" ? "active" : status === "completed" ? "complete" : "pending";
  const report: StageStatus = status === "completed" ? "complete" : "pending";

  return [
    { label: "Verification Checks", status: verification },
    { label: "Revenue Estimation", status: estimation },
    { label: "Report Generation", status: report },
  ];
}

interface ScanPipelineProps {
  status: AuditStatus;
  rulesCompleted?: number;
  rulesTotal?: number;
}

export function ScanPipeline({ status, rulesCompleted = 0, rulesTotal = 0 }: ScanPipelineProps) {
  const stages = buildStages(status);

  return (
    <section className="rounded-card border border-gray-100 bg-white p-8 shadow-card">
      <h2 className="text-h3 text-gray-900">Analysis Pipeline</h2>
      <ul className="mt-8 space-y-6">
        {stages.map((stage) => (
          <li key={stage.label} className="flex items-center gap-4">
            {stageIcon(stage.status)}
            <span className="text-body text-gray-700">{stage.label}</span>
          </li>
        ))}
      </ul>
      {status === "scanning" && rulesTotal > 0 && (
        <p className="mt-6 text-small text-gray-500">
          Running verification rules ({rulesCompleted} of {rulesTotal})…
        </p>
      )}
    </section>
  );
}
