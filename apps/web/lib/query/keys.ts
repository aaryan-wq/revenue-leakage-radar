export const queryKeys = {
  dashboard: ["dashboard"] as const,
  billing: ["billing"] as const,
  report: (reportId: string) => ["report", reportId] as const,
  reportFindings: (
    reportId: string,
    params: { pageSize: number; sort: string; category?: string },
  ) => ["report-findings", reportId, params] as const,
};
