import * as React from "react";
import { cn } from "@/lib/utils";

type AlertVariant = "default" | "destructive";

const variants: Record<AlertVariant, string> = {
  default: "border-border bg-card text-card-foreground",
  destructive: "border-destructive/25 bg-destructive/10 text-destructive"
};

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: AlertVariant;
}

export const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = "default", ...props }, ref) => (
    <div ref={ref} className={cn("rounded-md border p-3 text-sm leading-6", variants[variant], className)} {...props} />
  )
);
Alert.displayName = "Alert";
