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
    title: "Billing exports",
    description: "Any one file is enough to start. Upload more to unlock additional checks.",
    files: MINIMUM_BILLING_FILES,
  },
  {
    title: "Strongly recommended",
    description: "Unlocks subscription, invoice, and customer-level rules.",
    files: TIER_1_RECOMMENDED_FILES,
  },
  {
    title: "Optional",
    description: "Coupon and discount analysis.",
    files: TIER_2_OPTIONAL_FILES,
  },
  {
    title: "Power-ups",
    description: "CRM exports for contract and seat-count validation.",
    files: TIER_3_OPTIONAL_FILES,
  },
];

const FILE_GRID_CLASS =
  "mt-4 grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6";

function filenameHint(fileType: FileType): string | null {
  const names = FILE_TYPE_FILENAMES[fileType];
  if (!names || names.length === 0) return null;
  return names.join(" or ");
}

function FileChip({ fileType, isUploaded }: { fileType: FileType; isUploaded: boolean }) {
  const hint = filenameHint(fileType);

  return (
    <li
      className={`flex min-h-[4.25rem] items-start gap-2.5 rounded-lg border px-3 py-2.5 ${
        isUploaded ? "border-primary/25 bg-primary/5" : "border-line bg-secondary/20"
      }`}
    >
      <span className="mt-0.5 shrink-0">
        {isUploaded ? (
          <CheckCircle2 className="h-4 w-4 text-primary" strokeWidth={1.75} />
        ) : (
          <Circle className="h-4 w-4 text-muted-foreground/35" strokeWidth={1.75} />
        )}
      </span>
      <div className="min-w-0">
        <span
          className={`block text-sm leading-snug ${
            isUploaded ? "font-medium text-foreground" : "text-foreground"
          }`}
        >
          {FILE_TYPE_LABELS[fileType]}
        </span>
        {hint && (
          <p className="mt-0.5 line-clamp-2 text-[0.7rem] leading-snug text-muted-foreground">
            {hint}
          </p>
        )}
      </div>
    </li>
  );
}

function TierSectionBlock({
  section,
  uploadedTypes,
}: {
  section: TierSection;
  uploadedTypes: FileType[];
}) {
  return (
    <section className="border-t border-line pt-8 first:border-t-0 first:pt-0">
      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <h3 className="text-sm font-medium text-foreground">{section.title}</h3>
        <span className="text-xs text-muted-foreground tnum">
          {section.files.filter((file) => uploadedTypes.includes(file)).length}/{section.files.length}{" "}
          uploaded
        </span>
      </div>
      <p className="mt-1 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        {section.description}
      </p>
      <ul className={FILE_GRID_CLASS}>
        {section.files.map((fileType) => (
          <FileChip
            key={`${section.title}-${fileType}`}
            fileType={fileType}
            isUploaded={uploadedTypes.includes(fileType)}
          />
        ))}
      </ul>
    </section>
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

      <HairlineCard padding="sm" className="mt-10">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-[0.78rem] uppercase tracking-[0.16em] text-muted-foreground">
              Accepted exports
            </p>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground">
              Recognized CSV filenames for each export type. Upload any billing file to begin, then
              add more to unlock additional verification rules.
            </p>
          </div>
          {dataTier && hasUpload && (
            <div className="rounded-lg border border-line bg-secondary/30 px-4 py-3 text-right">
              <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                Data tier
              </p>
              <p className="mt-1 font-heading text-lg tracking-tight text-foreground">
                {DATA_TIER_LABELS[dataTier]}
              </p>
            </div>
          )}
        </div>

        <div className="mt-8">
          {TIER_SECTIONS.map((section) => (
            <TierSectionBlock key={section.title} section={section} uploadedTypes={uploadedTypes} />
          ))}
        </div>
      </HairlineCard>

      <p className="mt-6 text-sm leading-relaxed text-muted-foreground">
        Files are processed in an isolated environment and deleted after analysis. You can revoke
        access at any time.
      </p>
    </div>
  );
}

/** @deprecated Use DataTierFilesChecklist */
export const RequiredFilesChecklist = DataTierFilesChecklist;
