import * as React from "react";
import { cn } from "@/lib/utils";

type BadgeVariant = "default" | "secondary" | "outline" | "success" | "warning" | "destructive";

const variants: Record<BadgeVariant, string> = {
  default: "border-transparent bg-primary text-primary-foreground",
  secondary: "border-transparent bg-card text-foreground",
  outline: "border-border bg-background text-muted-foreground",
  success: "border-success/25 bg-success/10 text-body-strong",
  warning: "border-warning/25 bg-warning/10 text-body-strong",
  destructive: "border-destructive/25 bg-destructive/10 text-destructive"
};

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex h-7 items-center rounded-full border px-3 text-[13px] font-medium leading-none",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}
