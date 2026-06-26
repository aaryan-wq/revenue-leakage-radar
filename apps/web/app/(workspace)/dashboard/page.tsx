import { Suspense } from "react";

import { DashboardPageClient } from "@/components/dashboard/dashboard-page-client";

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-container px-8 py-20">
      <header className="mb-16">
        <p className="text-overline uppercase text-gray-500">Executive Workspace</p>
        <h1 className="mt-4 text-h1 text-gray-900">Dashboard</h1>
        <p className="mt-4 max-w-reading text-body text-gray-600">
          Your revenue verification overview — recoverable ARR, audit coverage, and next actions.
        </p>
      </header>
      <Suspense
        fallback={
          <div className="text-body text-gray-500">Loading executive workspace…</div>
        }
      >
        <DashboardPageClient />
      </Suspense>
    </div>
  );
}
