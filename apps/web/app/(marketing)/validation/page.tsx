import { ValidationPageClient } from "@/components/validation/validation-page-client";

export default function ValidationPage() {
  return (
    <div className="mx-auto max-w-container px-8 py-20">
      <div className="mb-16 max-w-reading">
        <p className="text-overline uppercase text-gray-500">Data Validation</p>
        <h1 className="mt-4 text-h1 text-primary">Validation</h1>
        <p className="mt-4 text-body text-gray-500">
          Review platform detection, column mapping, and validation results before scanning.
        </p>
      </div>
      <ValidationPageClient />
    </div>
  );
}
