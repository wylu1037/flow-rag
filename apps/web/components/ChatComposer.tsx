"use client";

import { PaperPlaneIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export function ChatComposer({
  value,
  disabled,
  onChange,
  onSubmit
}: {
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
}) {
  return (
    <form
      className="surface grid gap-3 rounded-lg p-3"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label className="grid gap-2">
        <span className="text-sm font-medium text-foreground">Question</span>
        <Textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          rows={3}
          placeholder="Ask about indexed documents"
        />
      </label>
      <div className="flex items-center justify-end">
        <Button
          type="submit"
          disabled={disabled}
        >
          <PaperPlaneIcon className="h-4 w-4" />
          Send
        </Button>
      </div>
    </form>
  );
}
