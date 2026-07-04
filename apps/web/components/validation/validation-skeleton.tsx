import { Skeleton } from "@/components/ui/skeleton";

export function ValidationSkeleton() {
  return (
    <div className="space-y-8">
      <div className="rounded-xl border border-line bg-secondary/40 p-6">
        <Skeleton className="h-5 w-48" />
        <Skeleton className="mt-3 h-4 w-full max-w-md" />
      </div>
      <div className="rounded-xl border border-line bg-card p-8">
        <Skeleton className="h-5 w-40" />
        <Skeleton className="mt-6 h-7 w-28 rounded-full" />
      </div>
      <div className="rounded-xl border border-line bg-card p-8">
        <Skeleton className="h-5 w-36" />
        <div className="mt-6 space-y-3">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      </div>
      <div className="rounded-xl border border-line bg-card p-8">
        <Skeleton className="h-5 w-44" />
        <div className="mt-6 space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      </div>
    </div>
  );
}
