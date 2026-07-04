import { Suspense } from "react";

import { HomePageClient } from "@/components/workspace/home-page-client";

export default function DashboardPage() {
  return (
    <Suspense fallback={null}>
      <HomePageClient />
    </Suspense>
  );
}
