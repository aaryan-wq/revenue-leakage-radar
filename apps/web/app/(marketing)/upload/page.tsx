import { UploadPageClient } from "@/components/upload/upload-page-client";

export default function UploadPage() {
  return (
    <div className="mx-auto max-w-container px-8 py-20">
      <div className="mb-12 max-w-reading">
        <p className="text-overline uppercase text-gray-500">Free Revenue Scan</p>
        <h1 className="mt-4 text-h1 text-primary">Upload Billing Data</h1>
        <p className="mt-4 text-body text-gray-500">
          Upload your billing CSV exports to begin a free revenue verification scan. No account required.
        </p>
      </div>
      <UploadPageClient />
    </div>
  );
}
