import { Suspense } from "react";

import { HomePageClient } from "@/components/workspace/home-page-client";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";

export default function DashboardPage() {
  return (
    <Suspense fallback={<PageLoadingSkeleton message="Loading workspace…" />}>
      <HomePageClient />
    </Suspense>
  );
}
