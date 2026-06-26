import { ReportPageClient } from "@/components/report/report-page-client";

export default function ReportPage() {
  return (
    <main className="mx-auto max-w-container px-8 py-20">
      <header className="mb-16 max-w-reading">
        <p className="text-overline uppercase text-gray-500">Consulting Report</p>
        <h1 className="mt-4 text-h1 text-gray-900">Detailed Report</h1>
        <p className="mt-4 text-body text-gray-600">
          Customer-level findings with invoice evidence and remediation guidance.
        </p>
      </header>
      <ReportPageClient />
    </main>
  );
}
