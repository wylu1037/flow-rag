import { ReaderIcon } from "@radix-ui/react-icons";

export function EmptyState({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="flex min-h-[220px] flex-col items-start justify-center rounded-lg border border-dashed border-border bg-card/70 p-6">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-md bg-accent text-primary">
        <ReaderIcon className="h-5 w-5" />
      </div>
      <h2 className="font-display text-[28px] leading-tight tracking-[-0.03em] text-ink">
        {title}
      </h2>
      <p className="mt-2 max-w-[52ch] text-sm leading-6 text-muted-foreground">{detail}</p>
    </div>
  );
}
