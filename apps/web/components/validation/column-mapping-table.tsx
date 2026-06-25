import { FILE_TYPE_LABELS, type FileType } from "@rlr/shared";

interface ColumnMappingTableProps {
  mappings: Record<string, Record<string, string>>;
}

export function ColumnMappingTable({ mappings }: ColumnMappingTableProps) {
  const entries = Object.entries(mappings);

  if (entries.length === 0) {
    return (
      <p className="text-small text-gray-500">No column mappings available yet.</p>
    );
  }

  return (
    <div className="space-y-6">
      {entries.map(([fileType, fileMappings]) => (
        <div key={fileType}>
          <h4 className="text-h4 text-gray-900">
            {FILE_TYPE_LABELS[fileType as FileType] ?? fileType}
          </h4>
          <div className="mt-3 overflow-hidden rounded-table border border-gray-100">
            <table className="w-full text-left">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-caption font-medium text-gray-500">Source</th>
                  <th className="px-4 py-3 text-caption font-medium text-gray-500">Canonical</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(fileMappings).map(([source, canonical]) => (
                  <tr key={source} className="border-t border-gray-100 hover:bg-gray-25">
                    <td className="px-4 py-3 text-small text-gray-700">{source}</td>
                    <td className="px-4 py-3 text-small font-medium text-gray-900">{canonical}</td>
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
