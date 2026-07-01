import type { Document } from "@/lib/types";
import { JobStatusBadge } from "./JobStatusBadge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";

export function DocumentTable({ documents }: { documents: Document[] }) {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-background">
      <ScrollArea orientation="horizontal">
        <Table className="min-w-[640px] table-fixed">
          <TableHeader>
            <TableRow className="bg-surface-soft hover:bg-surface-soft">
              <TableHead className="w-[330px]">File</TableHead>
              <TableHead className="w-[130px]">Status</TableHead>
              <TableHead className="w-[180px]">Created</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.map((document) => (
              <TableRow key={document.id}>
                <TableCell className="max-w-[330px]">
                  <div className="min-w-0">
                    <p className="truncate font-medium text-ink" title={document.filename}>
                      {document.filename}
                    </p>
                    <p
                      className="truncate font-mono text-xs text-muted-foreground"
                      title={document.content_hash}
                    >
                      {document.content_hash}
                    </p>
                  </div>
                </TableCell>
                <TableCell>
                  <JobStatusBadge status={document.status} />
                </TableCell>
                <TableCell>
                  <time className="text-xs text-muted-foreground">
                    {new Date(document.created_at).toLocaleString()}
                  </time>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </ScrollArea>
    </div>
  );
}
