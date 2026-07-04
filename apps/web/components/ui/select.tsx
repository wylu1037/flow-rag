"use client";

import * as React from "react";
import { CheckIcon, ChevronDownIcon } from "@radix-ui/react-icons";
import { cn } from "@/lib/utils";

export type SelectOption = {
  value: string;
  label: React.ReactNode;
  disabled?: boolean;
};

export type SelectProps = {
  value?: string;
  options: SelectOption[];
  onValueChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  name?: string;
  className?: string;
  triggerClassName?: string;
  contentClassName?: string;
  leadingIcon?: React.ReactNode;
  "aria-label"?: string;
  "aria-labelledby"?: string;
};

export function Select({
  value = "",
  options,
  onValueChange,
  placeholder = "Select an option",
  disabled = false,
  name,
  className,
  triggerClassName,
  contentClassName,
  leadingIcon,
  "aria-label": ariaLabel,
  "aria-labelledby": ariaLabelledBy
}: SelectProps) {
  const [open, setOpen] = React.useState(false);
  const rootRef = React.useRef<HTMLDivElement | null>(null);
  const listboxId = React.useId();
  const selected = options.find((option) => option.value === value);

  React.useEffect(() => {
    if (!open) {
      return;
    }

    function onPointerDown(event: PointerEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false);
      }
    }

    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);

    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  function choose(nextValue: string) {
    onValueChange(nextValue);
    setOpen(false);
  }

  return (
    <div ref={rootRef} className={cn("relative w-full min-w-0", className)}>
      {name ? <input type="hidden" name={name} value={value} /> : null}
      <button
        type="button"
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listboxId}
        aria-label={ariaLabel}
        aria-labelledby={ariaLabelledBy}
        data-state={open ? "open" : "closed"}
        className={cn(
          "flex h-10 w-full min-w-0 items-center justify-between gap-2 rounded-md border border-input bg-background px-3.5 text-sm text-foreground shadow-sm outline-none transition-[background-color,border-color,box-shadow,transform,opacity] hover:border-primary/60 hover:bg-secondary focus-visible:border-primary focus-visible:ring-4 focus-visible:ring-ring/15 active:translate-y-[1px] disabled:cursor-not-allowed disabled:opacity-50 data-[state=open]:border-primary data-[state=open]:bg-secondary data-[state=open]:ring-4 data-[state=open]:ring-ring/15",
          triggerClassName
        )}
        onClick={() => setOpen((current) => !current)}
        onKeyDown={(event) => {
          if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            setOpen(true);
          }
        }}
      >
        <span className="flex min-w-0 items-center gap-2">
          {leadingIcon ? (
            <span className="shrink-0 text-muted-foreground">{leadingIcon}</span>
          ) : null}
          <span className={cn("truncate", selected ? "text-foreground" : "text-muted-foreground")}>
            {selected?.label ?? placeholder}
          </span>
        </span>
        <ChevronDownIcon
          className={cn(
            "h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-150",
            open && "rotate-180 text-foreground"
          )}
        />
      </button>

      {open ? (
        <div
          id={listboxId}
          role="listbox"
          className={cn(
            "bg-popover text-popover-foreground absolute left-0 top-full z-50 mt-2 max-h-64 w-full overflow-y-auto rounded-md border border-border p-1 shadow-lg outline-none",
            contentClassName
          )}
        >
          {options.length === 0 ? (
            <div className="px-2.5 py-2 text-sm text-muted-foreground">No options</div>
          ) : (
            options.map((option) => {
              const active = option.value === value;

              return (
                <button
                  key={option.value}
                  type="button"
                  role="option"
                  aria-selected={active}
                  disabled={option.disabled}
                  className={cn(
                    "flex w-full min-w-0 items-center gap-2 rounded px-2.5 py-2 text-left text-sm outline-none transition-colors hover:bg-accent focus-visible:bg-accent disabled:pointer-events-none disabled:opacity-50",
                    active && "bg-accent text-accent-foreground"
                  )}
                  onClick={() => choose(option.value)}
                >
                  <span className="min-w-0 flex-1 truncate">{option.label}</span>
                  {active ? <CheckIcon className="h-4 w-4 shrink-0 text-primary" /> : null}
                </button>
              );
            })
          )}
        </div>
      ) : null}
    </div>
  );
}
