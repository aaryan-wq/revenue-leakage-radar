import { cn } from "@/lib/utils";

export function DeveloperDetailField({
  label,
  value,
  mono = false,
  className,
}: {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("space-y-1", className)}>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className={cn("text-sm", mono && "font-mono text-xs break-all")}>{value}</dd>
    </div>
  );
}

export function DeveloperDetailSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-4">
      <h2 className="font-heading text-lg tracking-tight">{title}</h2>
      {children}
    </section>
  );
}
