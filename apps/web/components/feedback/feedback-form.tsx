"use client";

import { useEffect, useState } from "react";
import { useUser } from "@clerk/nextjs";
import { AnalyticsEvents } from "@rlr/shared";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api";
import { captureEvent } from "@/lib/analytics/client";
import { submitFeedback, type FeedbackCategory } from "@/lib/feedback-api";
import { FEEDBACK_EMAIL } from "@/lib/feedback-email";
import { isClerkConfigured } from "@/lib/clerk";
import { toast } from "@/lib/toast";
import { cn } from "@/lib/utils";

const CATEGORIES: { value: FeedbackCategory; label: string }[] = [
  { value: "general", label: "General feedback" },
  { value: "bug", label: "Bug report" },
  { value: "feature", label: "Feature request" },
  { value: "billing", label: "Billing question" },
  { value: "other", label: "Other" },
];

const fieldClassName =
  "w-full rounded-lg border border-line bg-secondary/40 px-4 py-3 text-[0.92rem] text-foreground outline-none transition-shadow placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30";

const labelClassName = "mb-2 block text-[0.8rem] font-medium text-foreground";

interface FeedbackFormProps {
  source?: "modal" | "page" | "contact";
  onSuccess?: () => void;
  className?: string;
}

interface FeedbackFormFieldsProps extends FeedbackFormProps {
  initialName?: string;
  initialEmail?: string;
}

function FeedbackFormFields({
  source = "page",
  onSuccess,
  className,
  initialName = "",
  initialEmail = "",
}: FeedbackFormFieldsProps) {
  const [name, setName] = useState(initialName);
  const [email, setEmail] = useState(initialEmail);
  const [category, setCategory] = useState<FeedbackCategory>("general");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (initialName) setName(initialName);
  }, [initialName]);

  useEffect(() => {
    if (initialEmail) setEmail(initialEmail);
  }, [initialEmail]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting) return;

    setSubmitting(true);
    try {
      await submitFeedback({
        name: name.trim() || undefined,
        email: email.trim(),
        message: message.trim(),
        category,
        page_url: typeof window !== "undefined" ? window.location.href : undefined,
      });
      captureEvent(AnalyticsEvents.FEEDBACK_SUBMITTED, { source, category });
      toast.success("Thanks! We'll get back to you soon.");
      setMessage("");
      onSuccess?.();
    } catch (error) {
      const detail =
        error instanceof ApiError && error.message
          ? error.message
          : "Something went wrong. Please try again or email us directly.";
      toast.error(detail);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className={cn("space-y-5", className)} noValidate>
      <div className="grid gap-5 sm:grid-cols-2">
        <div>
          <label htmlFor={`feedback-name-${source}`} className={labelClassName}>
            Name <span className="text-muted-foreground">(optional)</span>
          </label>
          <input
            id={`feedback-name-${source}`}
            type="text"
            autoComplete="name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            className={fieldClassName}
            placeholder="Your name"
          />
        </div>
        <div>
          <label htmlFor={`feedback-email-${source}`} className={labelClassName}>
            Email
          </label>
          <input
            id={`feedback-email-${source}`}
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className={fieldClassName}
            placeholder="you@company.com"
          />
        </div>
      </div>

      <div>
        <label htmlFor={`feedback-category-${source}`} className={labelClassName}>
          Category
        </label>
        <select
          id={`feedback-category-${source}`}
          value={category}
          onChange={(event) => setCategory(event.target.value as FeedbackCategory)}
          className={fieldClassName}
        >
          {CATEGORIES.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor={`feedback-message-${source}`} className={labelClassName}>
          Message
        </label>
        <textarea
          id={`feedback-message-${source}`}
          required
          minLength={10}
          maxLength={5000}
          rows={source === "modal" ? 5 : 6}
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          className={cn(fieldClassName, "resize-y")}
          placeholder="Tell us what's on your mind — bugs, ideas, or anything we could do better."
        />
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <Button type="submit" disabled={submitting} className="sm:min-w-[160px]">
          {submitting ? "Sending…" : "Send feedback"}
        </Button>
        <p className="text-[0.8rem] text-muted-foreground">
          Prefer email?{" "}
          <a
            href={`mailto:${FEEDBACK_EMAIL}`}
            className="text-primary underline-offset-4 hover:underline"
          >
            Write to {FEEDBACK_EMAIL}
          </a>
        </p>
      </div>
    </form>
  );
}

function FeedbackFormWithClerk(props: FeedbackFormProps) {
  const { user, isLoaded } = useUser();
  const initialName = isLoaded ? (user?.firstName ?? user?.fullName ?? "") : "";
  const initialEmail = isLoaded ? (user?.primaryEmailAddress?.emailAddress ?? "") : "";

  return (
    <FeedbackFormFields
      {...props}
      initialName={initialName}
      initialEmail={initialEmail}
    />
  );
}

export function FeedbackForm(props: FeedbackFormProps) {
  if (isClerkConfigured()) {
    return <FeedbackFormWithClerk {...props} />;
  }

  return <FeedbackFormFields {...props} />;
}
