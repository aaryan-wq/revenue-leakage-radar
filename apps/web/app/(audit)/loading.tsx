export default function AuditFlowLoading() {
  return (
    <div
      className="mx-auto max-w-upload px-6 py-16 md:px-10"
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <span className="sr-only">Loading</span>
      <div className="h-3 w-40 rounded-lg bg-secondary/70">
        <div className="h-full w-full rounded-lg skeleton-shimmer" />
      </div>
      <div className="mt-6 h-12 w-full max-w-lg rounded-lg bg-secondary/70">
        <div className="h-full w-full rounded-lg skeleton-shimmer" />
      </div>
      <div className="mt-12 h-64 w-full rounded-xl border border-line bg-secondary/40">
        <div className="h-full w-full rounded-xl skeleton-shimmer" />
      </div>
    </div>
  );
}
