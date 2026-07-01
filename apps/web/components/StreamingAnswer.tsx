import type { ChatMessage } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";

export function StreamingAnswer({
  messages,
  loading,
  className
}: {
  messages: ChatMessage[];
  loading: boolean;
  className?: string;
}) {
  return (
    <ScrollArea
      className={cn("h-[420px] rounded-lg bg-surface-dark text-on-dark md:h-[520px]", className)}
      viewportClassName="flex flex-col gap-3 p-5"
    >
      {messages.length === 0 ? (
        <div className="flex h-full min-h-[340px] items-center justify-center text-center">
          <div>
            <p className="font-display text-[28px] leading-tight tracking-[-0.03em] text-on-dark">No messages yet</p>
            <p className="mt-3 max-w-[44ch] text-sm leading-6 text-on-dark-soft">
              Indexed documents will ground the first answer here.
            </p>
          </div>
        </div>
      ) : (
        messages.map((message) => (
          <article
            key={message.id}
            className={cn(
              "max-w-[86%] rounded-lg border px-4 py-3 text-sm leading-6",
              message.role === "user"
                ? "ml-auto border-primary bg-primary text-primary-foreground"
                : "mr-auto border-surface-dark-elevated bg-surface-dark-soft text-on-dark"
            )}
          >
            <p className="whitespace-pre-wrap">{message.content}</p>
          </article>
        ))
      )}
      {loading ? (
        <div className="mr-auto grid w-[min(520px,85%)] gap-2 rounded-lg border border-surface-dark-elevated bg-surface-dark-soft p-4">
          <Skeleton className="h-3 w-2/3 bg-on-dark-soft/25" />
          <Skeleton className="h-3 w-5/6 bg-on-dark-soft/20" />
          <Skeleton className="h-3 w-1/2 bg-on-dark-soft/20" />
        </div>
      ) : null}
    </ScrollArea>
  );
}
