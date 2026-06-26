import { cn } from "@/lib/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return <div className={cn("rounded-button skeleton-shimmer", className)} aria-hidden="true" {...props} />;
}

export function MetricCardSkeleton() {
  return (
    <div className="glass rounded-card p-8">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="mt-4 h-10 w-40" />
      <Skeleton className="mt-2 h-4 w-32" />
    </div>
  );
}

export function TableSkeleton({ rows = 8 }: { rows?: number }) {
  return (
    <div className="glass rounded-table overflow-hidden p-6">
      <Skeleton className="mb-4 h-4 w-full max-w-md" />
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" style={{ width: `${85 + (i % 3) * 5}%` }} />
        ))}
      </div>
    </div>
  );
}

export function PageLoadingSkeleton({ message }: { message: string }) {
  return (
    <div className="py-16">
      <p className="mb-8 text-body text-gray-500">{message}</p>
      <MetricCardSkeleton />
    </div>
  );
}
