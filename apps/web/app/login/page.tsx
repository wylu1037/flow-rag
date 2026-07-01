import { AppFrame } from "@/components/AppFrame";
import { StatusPill } from "@/components/StatusPill";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  return (
    <AppFrame>
      <section className="flex min-h-[calc(100dvh-9rem)] items-center rounded-lg bg-card p-6 md:p-8">
        <Card className="mx-auto w-full max-w-md">
          <CardHeader className="flex-row items-center justify-between gap-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.12em] text-primary">Access</p>
              <h1 className="font-display mt-2 text-[32px] leading-tight tracking-[-0.04em] text-ink">Demo tenant</h1>
            </div>
            <StatusPill label="enabled" tone="good" />
          </CardHeader>
          <CardContent>
          <label className="grid gap-2 text-sm">
            <span className="font-medium text-foreground">Email</span>
            <Input
              defaultValue="demo@flowrag.local"
            />
          </label>
          <Button className="mt-4 w-full">
            Continue
          </Button>
          </CardContent>
        </Card>
      </section>
    </AppFrame>
  );
}
