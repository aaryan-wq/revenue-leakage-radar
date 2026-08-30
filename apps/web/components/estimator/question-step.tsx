"use client";

import type { EstimatorQuestion } from "@rlr/shared";

import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";

interface QuestionStepProps {
  question: EstimatorQuestion;
  value: unknown;
  currency?: string;
  onChange: (value: unknown, currency?: string) => void;
  onContinue: () => void;
  isSubmitting?: boolean;
  error?: string | null;
}

export function QuestionStep({
  question,
  value,
  currency = "USD",
  onChange,
  onContinue,
  isSubmitting,
  error,
}: QuestionStepProps) {
  return (
    <HairlineCard padding="lg" className="space-y-8">
      <div className="space-y-2">
        <p className="text-overline text-muted-foreground">{question.section.replace("_", " ")}</p>
        <h2 className="text-h3 text-foreground">{question.label}</h2>
      </div>

      <div className="space-y-4">{renderInput(question, value, currency, onChange)}</div>

      {error ? <p className="text-small text-destructive">{error}</p> : null}

      <Button onClick={onContinue} disabled={isSubmitting} className="min-h-[44px] w-full sm:w-auto">
        {isSubmitting ? "Saving..." : "Continue"}
      </Button>
    </HairlineCard>
  );
}

function renderInput(
  question: EstimatorQuestion,
  value: unknown,
  currency: string,
  onChange: (value: unknown, currency?: string) => void,
) {
  switch (question.type) {
    case "boolean":
      return (
        <div className="flex flex-wrap gap-3">
          {[true, false].map((option) => (
            <Button
              key={String(option)}
              type="button"
              variant={value === option ? "primary" : "secondary"}
              onClick={() => onChange(option)}
              className="min-h-[44px]"
            >
              {option ? "Yes" : "No"}
            </Button>
          ))}
        </div>
      );
    case "select":
      return (
        <div className="grid gap-2">
          {(question.options ?? []).map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => onChange(option.value)}
              className={`rounded-xl border px-4 py-3 text-left text-body transition-colors min-h-[44px] ${
                value === option.value
                  ? "border-primary bg-secondary text-foreground"
                  : "border-border/60 bg-surface-glass-subtle text-muted-foreground hover:text-foreground"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      );
    case "multiselect": {
      const selected = Array.isArray(value) ? (value as string[]) : [];
      return (
        <div className="grid gap-2 sm:grid-cols-2">
          {(question.options ?? []).map((option) => {
            const active = selected.includes(option.value);
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => {
                  const next = active
                    ? selected.filter((v) => v !== option.value)
                    : [...selected, option.value];
                  onChange(next);
                }}
                className={`rounded-xl border px-4 py-3 text-left text-body transition-colors min-h-[44px] ${
                  active
                    ? "border-primary bg-secondary text-foreground"
                    : "border-border/60 bg-surface-glass-subtle text-muted-foreground hover:text-foreground"
                }`}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      );
    }
    case "number":
    case "currency":
      return (
        <div className="space-y-3">
          {question.type === "currency" ? (
            <select
              value={currency}
              onChange={(e) => onChange(value, e.target.value)}
              className="rounded-xl border border-border/60 bg-surface-glass-subtle px-4 py-3 text-body min-h-[44px]"
              aria-label="Currency"
            >
              {(question.currencies ?? ["USD"]).map((code) => (
                <option key={code} value={code}>
                  {code}
                </option>
              ))}
            </select>
          ) : null}
          <input
            type="number"
            min={question.min ?? 0}
            value={typeof value === "number" ? value : ""}
            onChange={(e) => onChange(Number(e.target.value), currency)}
            className="w-full rounded-xl border border-border/60 bg-surface-glass-subtle px-4 py-3 text-body tabular-nums min-h-[44px]"
            placeholder={question.type === "currency" ? "Annual recurring revenue" : "Enter a number"}
          />
        </div>
      );
    case "scale":
      return (
        <div className="space-y-3">
          <input
            type="range"
            min={question.min ?? 1}
            max={question.max ?? 5}
            value={typeof value === "number" ? value : question.min ?? 1}
            onChange={(e) => onChange(Number(e.target.value))}
            className="w-full"
            aria-label={question.label}
          />
          <div className="flex justify-between text-caption text-muted-foreground">
            <span>Not confident</span>
            <span className="tabular-nums text-foreground">{String(value ?? question.min ?? 1)}</span>
            <span>Extremely confident</span>
          </div>
        </div>
      );
    default:
      return null;
  }
}
