import {
  DATA_TIER_LABELS,
  FILE_TYPE_FILENAMES,
  FILE_TYPE_LABELS,
  MINIMUM_BILLING_FILES,
  TIER_1_RECOMMENDED_FILES,
  TIER_2_OPTIONAL_FILES,
  TIER_3_OPTIONAL_FILES,
  type CoverageAnalysis,
  type DataTier,
  type FileType,
} from "@rlr/shared";
import { CheckCircle2, Circle } from "lucide-react";

import { CoverageAnalysisPanel } from "@/components/upload/coverage-analysis-panel";
import { HairlineCard } from "@/components/ui/glass-card";

interface DataTierFilesChecklistProps {
  uploadedTypes: FileType[];
  dataTier?: DataTier;
  missingRecommended?: FileType[];
  coverage?: CoverageAnalysis | null;
}

interface TierSection {
  title: string;
  description: string;
  files: FileType[];
}

const TIER_SECTIONS: TierSection[] = [
  {
    title: "Billing Exports",
    description: "Any one file is enough to start. Upload more to unlock additional checks.",
    files: MINIMUM_BILLING_FILES,
  },
  {
    title: "Strongly Recommended",
    description: "Unlocks subscription, invoice, and customer-level rules.",
    files: TIER_1_RECOMMENDED_FILES,
  },
  {
    title: "Optional",
    description: "Coupon and discount analysis.",
    files: TIER_2_OPTIONAL_FILES,
  },
  {
    title: "Power-Ups",
    description: "CRM exports for contract and seat-count validation.",
    files: TIER_3_OPTIONAL_FILES,
  },
];

function filenameHint(fileType: FileType): string | null {
  const names = FILE_TYPE_FILENAMES[fileType];
  if (!names || names.length === 0) return null;
  return names.join(" or ");
}

function FileRow({ fileType, isUploaded }: { fileType: FileType; isUploaded: boolean }) {
  const hint = filenameHint(fileType);

  return (
    <li
      className={`flex items-start gap-3 rounded-lg border px-4 py-3 ${
        isUploaded ? "border-primary/25 bg-primary/5" : "border-line bg-card"
      }`}
    >
      <span className="mt-0.5 shrink-0">
        {isUploaded ? (
          <CheckCircle2 className="h-4 w-4 text-primary" strokeWidth={1.75} />
        ) : (
          <Circle className="h-4 w-4 text-muted-foreground/40" strokeWidth={1.75} />
        )}
      </span>
      <div className="min-w-0">
        <span
          className={`block text-sm leading-snug ${
            isUploaded ? "text-foreground" : "text-muted-foreground"
          }`}
        >
          {FILE_TYPE_LABELS[fileType]}
        </span>
        {hint && <p className="mt-1 truncate text-xs text-muted-foreground">{hint}</p>}
      </div>
    </li>
  );
}

export function DataTierFilesChecklist({
  uploadedTypes,
  dataTier,
  coverage,
}: DataTierFilesChecklistProps) {
  const hasUpload = uploadedTypes.length > 0;

  return (
    <div className="flex flex-col border-t border-line pt-10">
      <CoverageAnalysisPanel coverage={coverage} />

      {dataTier && hasUpload && (
        <HairlineCard padding="sm" className="mt-6">
          <p className="text-[0.78rem] uppercase tracking-[0.16em] text-muted-foreground">
            Data tier
          </p>
          <p className="mt-1 font-heading text-xl tracking-tight text-foreground">
            {DATA_TIER_LABELS[dataTier]}
          </p>
        </HairlineCard>
      )}

      <p className="mb-6 mt-10 text-[0.78rem] uppercase tracking-[0.16em] text-muted-foreground">
        Accepted exports
      </p>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {TIER_SECTIONS.map((section) => {
          const isBilling = section.title === "Billing Exports";
          return (
            <HairlineCard
              key={section.title}
              padding="sm"
              className={`h-full ${isBilling ? "md:col-span-2 xl:col-span-2" : ""}`}
            >
              <p className="text-[0.98rem] font-medium text-foreground">{section.title}</p>
              <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{section.description}</p>
              <ul
                className={`mt-4 grid gap-3 ${
                  isBilling ? "sm:grid-cols-2 lg:grid-cols-3" : "sm:grid-cols-2 xl:grid-cols-1"
                }`}
              >
                {section.files.map((fileType) => (
                  <FileRow
                    key={`${section.title}-${fileType}`}
                    fileType={fileType}
                    isUploaded={uploadedTypes.includes(fileType)}
                  />
                ))}
              </ul>
            </HairlineCard>
          );
        })}
      </div>

      <HairlineCard subtle padding="sm" className="mt-6">
        <p className="text-sm leading-relaxed text-muted-foreground">
          Files are processed in an isolated environment and deleted after analysis. You can revoke
          access at any time.
        </p>
      </HairlineCard>
    </div>
  );
}

/** @deprecated Use DataTierFilesChecklist */
export const RequiredFilesChecklist = DataTierFilesChecklist;
