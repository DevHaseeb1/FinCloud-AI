"use client";

import { TriangleAlert, AlertCircle, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useLatestAnomalies } from "@/hooks/useAnomalies";
import { formatCurrency } from "@/lib/format";
import type { Anomaly } from "@/types/apiTypes";

function severityIcon(sev?: string) {
  if (sev === "high") return <AlertTriangle className="size-4 text-red-500/70" />;
  if (sev === "medium") return <AlertCircle className="size-4 text-yellow-500/70" />;
  return <TriangleAlert className="size-4 text-blue-500/70" />;
}

function severityVariant(sev?: string) {
  if (sev === "high") return "destructive";
  if (sev === "medium") return "secondary";
  return "outline";
}

export function AnomalyPanel() {
  const q = useLatestAnomalies();

  return (
    <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-card/50 via-card/30 to-card/50 backdrop-blur-sm">
      <div className="absolute -right-32 -top-32 size-64 rounded-full bg-red-500/5 blur-3xl" />
      <CardHeader className="relative flex flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle className="flex items-center gap-2">
            <TriangleAlert className="size-4" />
            Latest Anomalies
          </CardTitle>
          <CardDescription>Detected cost anomalies in last 24 hours</CardDescription>
        </div>
        <Badge variant="outline" className="ml-auto">{q.data?.length ?? 0}</Badge>
      </CardHeader>
      <CardContent className="relative space-y-3">
        {q.isLoading ? (
          <>
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </>
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load anomalies.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No anomalies detected. Great job! 🎉</div>
        ) : (
          <div className="space-y-2">
            {q.data?.slice(0, 5).map((a: Anomaly, idx: number) => (
              <div
                key={String(a.id ?? idx)}
                className="relative flex items-start gap-3 rounded-lg border border-border/50 bg-background/50 p-3 transition-all hover:bg-background/80 hover:border-border"
              >
                <div className="mt-0.5 flex-shrink-0">
                  {severityIcon(a.severity)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <div className="truncate text-sm font-medium">
                      {a.service || "Unknown"}
                      {a.region && <span className="text-muted-foreground"> • {a.region}</span>}
                    </div>
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground line-clamp-2">
                    {a.description || a.timestamp || "No details"}
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    {typeof a.cost === "number" && (
                      <Badge variant="outline" className="text-xs">
                        {formatCurrency(a.cost, { currency: "USD" })}
                      </Badge>
                    )}
                    {typeof a.anomaly_score === "number" && (
                      <Badge variant="outline" className="text-xs">
                        Score: {(a.anomaly_score * 100).toFixed(0)}%
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <Badge variant={severityVariant(a.severity) as any} className="whitespace-nowrap">
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

