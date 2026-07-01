import type { Citation } from "@/lib/types";
import { ReaderIcon } from "@radix-ui/react-icons";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";

export function CitationList({ citations }: { citations: Citation[] }) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between gap-3 p-5">
        <CardTitle className="text-sm">Citations</CardTitle>
        <Badge variant="outline" className="font-mono">
          {citations.length}1
        </Badge>
      </CardHeader>
      <CardContent className="p-5 pt-0">
        <ScrollArea
          className="h-[190px] rounded-md"
          viewportClassName="grid gap-2"
        >
          {citations.length === 0 ? (
            <Alert className="border-dashed text-muted-foreground">
              No citations for the current answer.
            </Alert>
          ) : (
            citations.map((citation) => (
              <article
                key={citation.chunk_id}
                className="rounded-md border border-border bg-background p-3"
              >
                <div className="mb-2 flex items-start gap-2">
                  <ReaderIcon className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-ink">
                      {citation.filename}
                    </p>
                    <p className="font-mono text-xs text-muted-foreground">
                      {citation.section ?? "Document"} /{" "}
                      {citation.score.toFixed(3)}
                    </p>
                  </div>
                </div>
                <p className="line-clamp-4 text-xs leading-5 text-muted-foreground">
                  {citation.snippet}
                </p>
              </article>
            ))
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
