import { AnalysisPageClient } from "@/components/analysis/analysis-page-client";

export default function AnalysisPage() {
  return (
    <main className="mx-auto max-w-container px-8 py-20">
      <header className="mb-16 max-w-reading">
        <p className="text-overline uppercase text-gray-500">Processing</p>
        <h1 className="mt-4 text-h1 text-gray-900">Revenue Analysis</h1>
        <p className="mt-4 text-body text-gray-600">
          Running deterministic verification checks on your billing data.
        </p>
      </header>
      <AnalysisPageClient />
    </main>
  );
}
