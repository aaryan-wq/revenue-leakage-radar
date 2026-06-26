import { SummaryPageClient } from "@/components/summary/summary-page-client";

export default function SummaryPage() {
  return (
    <main className="mx-auto max-w-container px-8 py-20">
      <header className="mb-16 max-w-reading">
        <p className="text-overline uppercase text-gray-500">Free Summary</p>
        <h1 className="mt-4 text-h1 text-gray-900">Revenue Verification Summary</h1>
        <p className="mt-4 text-body text-gray-600">
          Evidence-backed overview of recoverable recurring revenue in your billing data.
        </p>
      </header>
      <SummaryPageClient />
    </main>
  );
}
