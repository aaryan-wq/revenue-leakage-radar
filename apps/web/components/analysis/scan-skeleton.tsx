import { Skeleton } from "@/components/ui/skeleton";

export function ScanSkeleton() {
  return (
    <div className="mx-auto flex max-w-processing flex-col items-center py-8">
      <div className="relative mb-16 flex h-56 w-56 items-center justify-center rounded-full border border-line bg-card">
        <Skeleton className="h-12 w-16 rounded-lg" />
      </div>
      <div className="w-full max-w-sm space-y-3">
        <Skeleton className="mx-auto h-6 w-48" />
        <Skeleton className="mx-auto h-4 w-64" />
      </div>
      <div className="mt-12 flex items-center gap-2.5">
        {Array.from({ length: 5 }).map((_, index) => (
          <Skeleton key={index} className="h-1 w-8 rounded-full" />
        ))}
      </div>
    </div>
  );
}
