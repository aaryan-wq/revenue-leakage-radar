"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { EstimatorQuestion } from "@rlr/shared";

import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";

interface QuestionStepProps {
  question: EstimatorQuestion;
  sectionLabel: string;
  value: unknown;
  currency?: string;
  onChange: (value: unknown, currency?: string) => void;
  onContinue: () => void;
  isSubmitting?: boolean;
  error?: string | null;
}

export function QuestionStep({
  question,
  sectionLabel,
  value,
  currency = "USD",
  onChange,
  onContinue,
  isSubmitting,
  error,
}: QuestionStepProps) {
  const reducedMotion = useReducedMotion();

  return (
    <motion.div
      key={question.id}
      initial={reducedMotion ? false : { opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
    >
      <HairlineCard padding="lg" className="mx-auto max-w-readable space-y-8">
        <div className="space-y-3">
          <p className="text-overline text-muted-foreground">{sectionLabel}</p>
          <h2 className="text-h3 text-foreground">{question.label}</h2>
        </div>

        <div className="space-y-3">{renderInput(question, value, currency, onChange)}</div>

        {error ? <p className="text-small text-destructive">{error}</p> : null}

        <Button onClick={onContinue} disabled={isSubmitting} className="min-h-[44px] w-full sm:w-auto">
          {isSubmitting ? "Saving..." : "Continue"}
        </Button>
      </HairlineCard>
    </motion.div>
  );
}

function optionClass(active: boolean): string {
  return active
    ? "border-primary/60 bg-secondary text-foreground shadow-sm"
    : "border-border/50 bg-surface-glass-subtle text-muted-foreground hover:border-border hover:text-foreground";
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
              className="min-h-[44px] min-w-[120px]"
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
              className={`rounded-xl border px-5 py-4 text-left text-body transition-all min-h-[44px] ${optionClass(value === option.value)}`}
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
                className={`rounded-xl border px-5 py-4 text-left text-body transition-all min-h-[44px] ${optionClass(active)}`}
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
              className="rounded-xl border border-border/50 bg-surface-glass-subtle px-4 py-3 text-body min-h-[44px]"
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
            className="w-full rounded-xl border border-border/50 bg-surface-glass-subtle px-4 py-3 text-body tabular-nums min-h-[44px] focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/20"
            placeholder={question.type === "currency" ? "Annual recurring revenue" : "Enter a number"}
          />
        </div>
      );
    case "scale":
      return (
        <div className="space-y-4 rounded-xl border border-border/50 bg-surface-glass-subtle px-5 py-6">
          <input
            type="range"
            min={question.min ?? 1}
            max={question.max ?? 5}
            value={typeof value === "number" ? value : question.min ?? 1}
            onChange={(e) => onChange(Number(e.target.value))}
            className="w-full accent-primary"
            aria-label={question.label}
          />
          <div className="flex justify-between text-caption text-muted-foreground">
            <span>Not confident</span>
            <span className="tabular-nums text-foreground">{String(value ?? question.min ?? 1)}</span>
            <span>Very confident</span>
          </div>
        </div>
      );
    default:
      return null;
  }
}
