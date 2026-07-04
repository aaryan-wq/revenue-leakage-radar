export const queryKeys = {
  dashboard: ["dashboard"] as const,
  billing: ["billing"] as const,
  report: (reportId: string) => ["report", reportId] as const,
};
