import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef, type HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex h-6 items-center rounded-md px-2 text-xs font-medium",
  {
    variants: {
      variant: {
        success: "bg-primary/10 text-primary",
        warning: "bg-leak/10 text-leak",
        error: "bg-destructive/10 text-destructive",
        info: "bg-secondary text-muted-foreground",
        gray: "bg-secondary text-muted-foreground",
        leak: "bg-leak/10 text-leak",
        elevated: "bg-primary/10 text-primary",
        monitor: "bg-muted text-muted-foreground",
      },
    },
    defaultVariants: {
      variant: "gray",
    },
  },
);

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant, ...props }, ref) => (
    <span ref={ref} className={cn(badgeVariants({ variant }), className)} {...props} />
  ),
);

Badge.displayName = "Badge";
