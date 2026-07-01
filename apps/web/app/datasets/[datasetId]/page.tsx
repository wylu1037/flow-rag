import { AppFrame } from "@/components/AppFrame";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function DatasetDetailPage({ params }: { params: { datasetId: string } }) {
  return (
    <AppFrame>
      <Card>
        <CardHeader>
          <Badge variant="secondary" className="w-fit uppercase tracking-[0.12em]">Dataset</Badge>
          <h1 className="font-display text-[40px] leading-[1.08] tracking-[-0.04em] text-ink md:text-[48px]">
            {params.datasetId}
          </h1>
        </CardHeader>
        <CardContent>
        <p className="max-w-[68ch] text-base leading-[1.55] text-body">
          Dataset-level document and eval views will attach here as the storage layer moves from the local MVP to Postgres.
        </p>
        </CardContent>
      </Card>
    </AppFrame>
  );
}
