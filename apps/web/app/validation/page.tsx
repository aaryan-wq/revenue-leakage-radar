import { ValidationPageClient } from "@/components/validation/validation-page-client";

export default function ValidationPage() {
  return (
    <div className="mx-auto max-w-container px-8 py-16">
      <div className="mb-12 max-w-reading">
        <h1 className="text-h1 text-primary">Validation</h1>
        <p className="mt-4 text-body text-gray-500">
          Review platform detection, column mapping, and validation results before scanning.
        </p>
      </div>
      <ValidationPageClient />
    </div>
  );
}
