export const queryKeys = {
  dashboard: ["dashboard"] as const,
  billing: ["billing"] as const,
  adminMe: ["admin", "me"] as const,
  adminOverview: ["admin", "overview"] as const,
  adminAudits: (params: { q?: string; page?: number }) => ["admin", "audits", params] as const,
  adminReports: (params: { q?: string; purchased?: boolean; page?: number }) =>
    ["admin", "reports", params] as const,
  adminLogs: (params: { page?: number }) => ["admin", "logs", params] as const,
  adminNotes: (params: { page?: number }) => ["admin", "notes", params] as const,
  report: (reportId: string) => ["report", reportId] as const,
  reportFindings: (
    reportId: string,
    params: { pageSize: number; sort: string; category?: string },
  ) => ["report-findings", reportId, params] as const,
};
