import { Suspense } from "react";

import { UploadPageClient } from "@/components/upload/upload-page-client";
import { DelayedPageFallback } from "@/components/ui/page-loading";

export default function UploadPage() {
  return (
    <Suspense fallback={<DelayedPageFallback message="Preparing upload session…" variant="default" />}>
      <UploadPageClient />
    </Suspense>
  );
}
