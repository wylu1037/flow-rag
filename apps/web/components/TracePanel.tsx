import type { TracePayload } from "@/lib/types";
import { StopwatchIcon } from "@radix-ui/react-icons";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";

export function TracePanel({ trace }: { trace: TracePayload | null }) {
  const steps = trace?.flow_steps ?? [];
  return (
    <Card className="border-surface-dark bg-surface-dark text-on-dark">
      <CardHeader className="flex-row items-center justify-between gap-3">
        <CardTitle className="text-sm text-on-dark">Trace</CardTitle>
        <Badge className="border-surface-dark-elevated bg-surface-dark-elevated font-mono text-on-dark">
          {trace?.latency_ms ?? 0} ms
        </Badge>
      </CardHeader>
      <CardContent>
      {steps.length === 0 ? (
        <Alert className="border-surface-dark-elevated bg-surface-dark-soft text-on-dark-soft">
          No trace captured yet.
        </Alert>
      ) : (
        <div className="divide-y divide-surface-dark-elevated rounded-md border border-surface-dark-elevated bg-surface-dark-soft">
          {steps.map((step) => (
            <div key={`${step.node}-${step.latency_ms}`} className="flex items-center gap-3 px-3 py-2">
              <StopwatchIcon className="h-4 w-4 shrink-0 text-primary" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium text-on-dark">{step.node}</p>
                <p className="font-mono text-[11px] text-on-dark-soft">{step.status}</p>
              </div>
              <span className="font-mono text-xs text-on-dark-soft">{step.latency_ms}</span>
            </div>
          ))}
        </div>
      )}
      </CardContent>
    </Card>
  );
}
