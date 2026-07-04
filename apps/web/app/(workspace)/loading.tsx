export default function WorkspaceLoading() {
  return (
    <div
      className="mx-auto max-w-marketing px-6 py-16 md:px-10"
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <span className="sr-only">Loading workspace</span>
      <div className="h-3 w-36 rounded-lg bg-secondary/70">
        <div className="h-full w-full rounded-lg skeleton-shimmer" />
      </div>
      <div className="mt-6 h-14 w-full max-w-xl rounded-lg bg-secondary/70">
        <div className="h-full w-full rounded-lg skeleton-shimmer" />
      </div>
      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="rounded-xl border border-line bg-card p-8">
            <div className="h-3 w-24 rounded-lg bg-secondary/70">
              <div className="h-full w-full rounded-lg skeleton-shimmer" />
            </div>
            <div className="mt-4 h-10 w-32 rounded-lg bg-secondary/70">
              <div className="h-full w-full rounded-lg skeleton-shimmer" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
