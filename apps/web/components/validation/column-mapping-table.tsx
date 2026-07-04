import { FILE_TYPE_LABELS, type FileType } from "@rlr/shared";

interface ColumnMappingTableProps {
  mappings: Record<string, Record<string, string>>;
}

export function ColumnMappingTable({ mappings }: ColumnMappingTableProps) {
  const entries = Object.entries(mappings);

  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">No column mappings available yet.</p>;
  }

  return (
    <div className="space-y-8">
      {entries.map(([fileType, fileMappings]) => (
        <div key={fileType}>
          <h4 className="font-heading text-lg tracking-tight text-foreground">
            {FILE_TYPE_LABELS[fileType as FileType] ?? fileType}
          </h4>
          <div className="mt-4 overflow-hidden rounded-xl border border-line bg-card">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-line">
                  <th className="px-5 py-3 text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    Source
                  </th>
                  <th className="px-5 py-3 text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    Canonical
                  </th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(fileMappings).map(([source, canonical]) => (
                  <tr key={source} className="border-t border-line transition-colors hover:bg-secondary/30">
                    <td className="px-5 py-3 text-sm text-muted-foreground">{source}</td>
                    <td className="px-5 py-3 text-sm font-medium text-foreground">{canonical}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
