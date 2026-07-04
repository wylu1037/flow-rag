import { ReaderIcon } from "@radix-ui/react-icons";
import type { ComponentType } from "react";
import { cn } from "@/lib/utils";

type EmptyStateProps = {
  title: string;
  detail: string;
  icon?: ComponentType<{ className?: string }>;
  compact?: boolean;
  variant?: "default" | "dark";
  className?: string;
};

export function EmptyState({
  title,
  detail,
  icon: Icon = ReaderIcon,
  compact = false,
  variant = "default",
  className
}: EmptyStateProps) {
  const dark = variant === "dark";

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-lg border border-dashed text-center",
        compact ? "min-h-[150px] p-4" : "min-h-[220px] p-6",
        dark ? "border-surface-dark-elevated bg-surface-dark-soft" : "border-border bg-card/70",
        className
      )}
    >
      <div
        className={cn(
          "flex items-center justify-center rounded-md text-primary",
          compact ? "mb-3 h-9 w-9" : "mb-4 h-10 w-10",
          dark ? "bg-surface-dark-elevated" : "bg-accent"
        )}
      >
        <Icon className={compact ? "h-4 w-4" : "h-5 w-5"} />
      </div>
      <h2
        className={cn(
          "font-display leading-tight",
          compact ? "text-sm font-medium" : "text-[28px] tracking-[-0.03em]",
          dark ? "text-on-dark" : "text-ink"
        )}
      >
        {title}
      </h2>
      <p
        className={cn(
          "mt-2 max-w-[52ch] leading-6",
          compact ? "text-xs" : "text-sm",
          dark ? "text-on-dark-soft" : "text-muted-foreground"
        )}
      >
        {detail}
      </p>
    </div>
  );
}
