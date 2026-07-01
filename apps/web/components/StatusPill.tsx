import { Badge } from "@/components/ui/badge";

type Tone = "neutral" | "good" | "warn" | "bad";

const tones: Record<Tone, "outline" | "success" | "warning" | "destructive"> = {
  neutral: "outline",
  good: "success",
  warn: "warning",
  bad: "destructive"
};

export function StatusPill({ label, tone = "neutral" }: { label: string; tone?: Tone }) {
  return <Badge variant={tones[tone]}>{label}</Badge>;
}
