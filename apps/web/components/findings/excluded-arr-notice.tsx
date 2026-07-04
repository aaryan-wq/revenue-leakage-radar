import Link from "next/link";

import type { FindingResponse } from "@rlr/shared";

interface ExcludedArrNoticeProps {
  finding: FindingResponse;
  className?: string;
}

export function ExcludedArrNotice({ finding, className = "" }: ExcludedArrNoticeProps) {
  if (finding.attribution !== "secondary") {
    return null;
  }

  return (
    <p className={`max-w-2xl text-sm leading-relaxed text-muted-foreground ${className}`}>
      Excluded from headline recoverable ARR to avoid double-counting the same leakage.
      {finding.primary_finding_title ? (
        <>
          {" "}
          Counted under{" "}
          {finding.primary_finding_id ? (
            <Link
              href={`/findings/${finding.primary_finding_id}`}
              className="font-medium text-foreground underline-offset-4 hover:underline"
            >
              {finding.primary_finding_title}
            </Link>
          ) : (
            <span className="font-medium text-foreground">{finding.primary_finding_title}</span>
          )}
          .
        </>
      ) : null}
    </p>
  );
}
