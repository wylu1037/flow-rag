"use client";

import { PaperPlaneIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

export function ChatComposer({
  value,
  disabled,
  onChange,
  onSubmit,
  className
}: {
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
  className?: string;
}) {
  return (
    <form
      className={cn("surface rounded-lg p-3", className)}
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label className="grid gap-2">
        <span className="text-sm font-medium text-foreground">Question</span>
        <span className="relative block">
          <Textarea
            value={value}
            onChange={(event) => onChange(event.target.value)}
            rows={3}
            placeholder="Ask about indexed documents"
            className="min-h-[104px] pr-16"
          />
          <Button
            type="submit"
            size="icon"
            disabled={disabled}
            aria-label="Send message"
            className="absolute bottom-3 right-3 h-10 w-10"
          >
            <PaperPlaneIcon className="h-4 w-4" />
          </Button>
        </span>
      </label>
    </form>
  );
}
