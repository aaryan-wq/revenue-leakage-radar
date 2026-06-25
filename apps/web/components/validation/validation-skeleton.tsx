export function ValidationSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-24 rounded-card bg-gray-100" />
      <div className="h-8 w-48 rounded bg-gray-100" />
      <div className="space-y-3">
        <div className="h-16 rounded-card bg-gray-100" />
        <div className="h-16 rounded-card bg-gray-100" />
        <div className="h-16 rounded-card bg-gray-100" />
      </div>
      <div className="h-64 rounded-card bg-gray-100" />
    </div>
  );
}
