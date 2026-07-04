import type { ReactNode } from "react";

type LegalSectionProps = {
  title: string;
  children: ReactNode;
};

export function LegalSection({ title, children }: LegalSectionProps) {
  return (
    <section>
      <h2 className="font-heading text-xl tracking-tight">{title}</h2>
      <div className="mt-3 space-y-3 leading-relaxed text-muted-foreground">{children}</div>
    </section>
  );
}

type LegalSubsectionProps = {
  title: string;
  children: ReactNode;
};

export function LegalSubsection({ title, children }: LegalSubsectionProps) {
  return (
    <div className="mt-4">
      <h3 className="font-heading text-lg tracking-tight text-foreground">{title}</h3>
      <div className="mt-2 space-y-3">{children}</div>
    </div>
  );
}

export function LegalList({ items }: { items: ReactNode[] }) {
  return (
    <ul className="list-disc space-y-2 pl-6">
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );
}

export function LegalOrderedList({ items }: { items: ReactNode[] }) {
  return (
    <ol className="list-decimal space-y-2 pl-6">
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ol>
  );
}

export function LegalStrong({ children }: { children: ReactNode }) {
  return <strong className="font-medium text-foreground">{children}</strong>;
}
