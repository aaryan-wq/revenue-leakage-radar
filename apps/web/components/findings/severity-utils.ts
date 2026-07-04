export function getSeverityLabel(severity: string): string {
  const normalized = severity.toLowerCase();
  if (normalized === "critical") return "Critical";
  if (normalized === "high") return "Elevated";
  return "Monitor";
}

export function getSeverityTextClass(severity: string): string {
  const normalized = severity.toLowerCase();
  if (normalized === "critical") return "text-leak";
  if (normalized === "high") return "text-primary";
  return "text-muted-foreground";
}

export function getSeverityDotClass(severity: string): string {
  const normalized = severity.toLowerCase();
  if (normalized === "critical") return "bg-leak";
  if (normalized === "high") return "bg-primary";
  return "bg-muted-foreground/50";
}
