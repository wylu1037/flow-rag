import { StatusPill } from "./StatusPill";

export function JobStatusBadge({ status }: { status: string }) {
  const tone =
    status === "indexed" || status === "succeeded"
      ? "good"
      : status === "failed"
        ? "bad"
        : status === "uploaded"
          ? "warn"
          : "neutral";

  return <StatusPill label={status} tone={tone} />;
}
