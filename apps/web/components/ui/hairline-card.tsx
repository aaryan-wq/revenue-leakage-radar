import { forwardRef, type HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type HairlineCardProps = HTMLAttributes<HTMLDivElement> & {
  elevated?: boolean;
  subtle?: boolean;
  interactive?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
};

const paddingMap = {
  none: "",
  sm: "p-5",
  md: "p-8",
  lg: "p-10",
};

export const HairlineCard = forwardRef<HTMLDivElement, HairlineCardProps>(
  (
    {
      className,
      elevated = false,
      subtle = false,
      interactive = false,
      padding = "md",
      children,
      ...props
    },
    ref,
  ) => {
    const surfaceClass = elevated
      ? "bg-card border-line"
      : subtle
        ? "bg-secondary/40 border-line"
        : "bg-card border-line";

    return (
      <div
        ref={ref}
        className={cn(
          "rounded-xl border transition-[background-color,border-color] duration-normal ease-glide motion-reduce:transition-none",
          surfaceClass,
          interactive && "hover:border-foreground/20 hover:bg-secondary",
          paddingMap[padding],
          className,
        )}
        {...props}
      >
        {children}
      </div>
    );
  },
);

HairlineCard.displayName = "HairlineCard";

/** @deprecated Use HairlineCard */
export const GlassCard = HairlineCard;
