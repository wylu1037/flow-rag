import { AppFrame } from "@/components/AppFrame";
import { StatusPill } from "@/components/StatusPill";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <AppFrame>
      <Card>
        <CardHeader>
          <Badge variant="secondary" className="w-fit font-mono uppercase">
            Settings
          </Badge>
          <CardTitle className="font-display text-[40px] leading-[1.08] tracking-[-0.04em] md:text-[48px]">
            Runtime controls
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <RuntimeItem label="Max retrieval rounds" value="3" />
            <RuntimeItem label="Max rewritten queries" value="3" />
            <RuntimeItem label="Evidence chunks" value="10" />
            <RuntimeItem label="Provider mode" value="local" />
          </div>
          <div className="mt-6 rounded-lg border border-border bg-background p-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-sm font-medium text-ink">LLM provider</h2>
                <p className="mt-1 text-sm leading-6 text-muted-foreground">
                  The current MVP uses a deterministic local answerer until provider keys are
                  configured.
                </p>
              </div>
              <StatusPill label="local" tone="good" />
            </div>
          </div>
        </CardContent>
      </Card>
    </AppFrame>
  );
}

function RuntimeItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-background p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 font-display text-[28px] leading-tight tracking-[-0.03em] text-ink">
        {value}
      </p>
    </div>
  );
}
