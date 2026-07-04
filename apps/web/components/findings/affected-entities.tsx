import type { FindingResponse } from "@rlr/shared";

interface AffectedEntitiesProps {
  finding: FindingResponse;
  className?: string;
}

export function AffectedEntities({ finding, className = "" }: AffectedEntitiesProps) {
  const entities = [
    { label: "Customer", value: finding.customer_id },
    { label: "Subscription", value: finding.subscription_id },
    { label: "Invoice", value: finding.invoice_id },
  ].filter((entity) => Boolean(entity.value));

  if (entities.length === 0) {
    return null;
  }

  return (
    <div className={className}>
      <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
        Affected entities
      </p>
      <p className="mt-1 text-xs text-muted-foreground">
        IDs from your uploaded billing and CRM files
      </p>
      <div className="mt-4 flex flex-wrap gap-x-10 gap-y-4">
        {entities.map((entity) => (
          <div key={entity.label}>
            <p className="text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
              {entity.label}
            </p>
            <p className="mt-1 font-mono text-sm text-foreground">{entity.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
