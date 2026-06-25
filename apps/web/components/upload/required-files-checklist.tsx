import { FILE_TYPE_LABELS, REQUIRED_BILLING_FILES, type FileType } from "@rlr/shared";
import { CheckCircle2, Circle } from "lucide-react";

interface RequiredFilesChecklistProps {
  uploadedTypes: FileType[];
}

export function RequiredFilesChecklist({ uploadedTypes }: RequiredFilesChecklistProps) {
  return (
    <div className="rounded-card border border-gray-100 bg-white p-8 shadow-card">
      <h3 className="text-h4 text-gray-900">Required Billing Files</h3>
      <p className="mt-2 text-small text-gray-500">
        Upload all five billing exports to continue to validation.
      </p>
      <ul className="mt-6 space-y-4">
        {REQUIRED_BILLING_FILES.map((fileType) => {
          const isUploaded = uploadedTypes.includes(fileType);
          return (
            <li key={fileType} className="flex items-center gap-3">
              {isUploaded ? (
                <CheckCircle2 className="h-5 w-5 text-success" strokeWidth={1.75} />
              ) : (
                <Circle className="h-5 w-5 text-gray-300" strokeWidth={1.75} />
              )}
              <span className={isUploaded ? "text-body text-gray-900" : "text-body text-gray-500"}>
                {FILE_TYPE_LABELS[fileType]}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
