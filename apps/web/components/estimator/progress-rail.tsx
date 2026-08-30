"use client";

interface SectionMeta {
  id: string;
  label: string;
}

interface ProgressRailProps {
  sections: SectionMeta[];
  currentSection: string | null;
  estimatedSecondsRemaining: number;
}

export function ProgressRail({ sections, currentSection, estimatedSecondsRemaining }: ProgressRailProps) {
  const currentIndex = sections.findIndex((s) => s.id === currentSection);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <p className="text-overline text-muted-foreground">Billing Profile</p>
        <p className="text-caption text-muted-foreground">
          About {Math.max(1, Math.ceil(estimatedSecondsRemaining / 60))} min remaining
        </p>
      </div>
      <div className="flex items-center gap-2">
        {sections.map((section, index) => {
          const complete = currentIndex > index;
          const active = section.id === currentSection;
          return (
            <div key={section.id} className="flex flex-1 items-center gap-2">
              <div
                className={`h-2 flex-1 rounded-full transition-colors ${
                  complete || active ? "bg-primary" : "bg-border/50"
                }`}
                title={section.label}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
