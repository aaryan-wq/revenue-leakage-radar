import { AnalysisPageClient } from "@/components/analysis/analysis-page-client";

export default function AnalysisPage() {
  return (
    <main className="mx-auto max-w-content px-6 py-16">
      <header className="mb-12">
        <h1 className="text-h1 text-gray-900">Revenue Analysis</h1>
        <p className="mt-4 text-body text-gray-600">
          Running deterministic verification checks on your billing data.
        </p>
      </header>
      <AnalysisPageClient />
    </main>
  );
}
