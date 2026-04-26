"use client";

import { TriangleAlert } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useLatestAnomalies } from "@/hooks/useAnomalies";

function severityVariant(sev?: string) {
  if (sev === "high") return "destructive";
  if (sev === "medium") return "secondary";
  return "outline";
}

export function AnomalyPanel() {
  const q = useLatestAnomalies();

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="flex items-center gap-2">
          <TriangleAlert className="size-4 text-muted-foreground" /> Latest Anomalies
        </CardTitle>
        <Badge variant="outline">{q.data?.length ?? 0}</Badge>
      </CardHeader>
      <CardContent className="space-y-3">
        {q.isLoading ? (
          <>
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </>
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load anomalies.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No anomalies detected.</div>
        ) : (
          <div className="grid gap-2">
            {q.data?.slice(0, 5).map((a, idx) => (
              <div
                key={String(a.id ?? idx)}
                className="flex items-center justify-between rounded-md border p-3"
              >
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium">
                    {a.service || "Unknown service"}{" "}
                    <span className="text-muted-foreground">
                      {a.region ? `• ${a.region}` : ""}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground truncate">
                    {a.description || a.timestamp || "No details provided"}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {typeof a.anomaly_score === "number" ? (
                    <Badge variant="outline">Score {a.anomaly_score.toFixed(2)}</Badge>
                  ) : null}
                  <Badge variant={severityVariant(a.severity) as any}>
                    {a.severity ?? "low"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

