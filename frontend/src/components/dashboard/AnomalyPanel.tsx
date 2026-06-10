"use client";

import * as React from "react";
import { TriangleAlert, AlertCircle, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useLatestAnomalies } from "@/hooks/useAnomalies";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { formatCurrency } from "@/lib/format";
import { staggerDelay } from "@/lib/animations";
import { cn } from "@/lib/utils";
import type { Anomaly } from "@/types/apiTypes";

function severityIcon(sev?: string) {
  if (sev === "high") return <AlertTriangle className="size-4 text-ember/70" />;
  if (sev === "medium") return <AlertCircle className="size-4 text-yellow-500/70" />;
  return <TriangleAlert className="size-4 text-cyan/70" />;
}

function severityVariant(sev?: string) {
  if (sev === "high") return "destructive";
  if (sev === "medium") return "secondary";
  return "outline";
}

function AnomalyRow({ a, idx, reduced }: { a: Anomaly; idx: number; reduced: boolean }) {
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    const delay = idx < 5 ? staggerDelay(idx, 40) : 0;
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [idx]);

  return (
    <div
      className={cn(
        "relative flex items-start gap-3 rounded-lg border border-border/50 bg-background/50 p-3 transition-all duration-100 hover:bg-background/80 hover:border-border",
        !visible && "opacity-0 translate-y-2",
        visible && "opacity-100 translate-y-0",
      )}
      style={{
        transitionTimingFunction: "var(--ease-out-expo)",
        transitionDuration: "250ms",
        transitionDelay: visible ? "0ms" : "0ms",
      }}
    >
      {a.severity === "high" && (
        <span
          className={cn(
            "absolute left-0 top-1 bottom-0 w-0.5 rounded-full bg-ember",
            !reduced && "animate-anomaly-pulse",
          )}
        />
      )}
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
            <Badge variant="outline" className="text-xs font-mono">
              {formatCurrency(a.cost, { currency: "USD" })}
            </Badge>
          )}
          {typeof a.anomaly_score === "number" && (
            <Badge variant="outline" className="text-xs font-mono">
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
  );
}

export function AnomalyPanel() {
  const q = useLatestAnomalies();
  const reduced = useReducedMotion();

  return (
    <Card className="relative overflow-hidden border-border/50 bg-surface/80 backdrop-blur-sm">
      <div className="absolute -right-32 -top-32 size-64 rounded-full bg-ember/5 blur-3xl pointer-events-none" />
      <CardHeader className="relative flex flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle className="flex items-center gap-2">
            <TriangleAlert className="size-4 text-ember" />
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
          <div className="text-sm text-muted-foreground">No anomalies detected. Great job!</div>
        ) : (
          <div className="space-y-2">
            {q.data?.slice(0, 5).map((a: Anomaly, idx: number) => (
              <AnomalyRow key={String(a.id ?? idx)} a={a} idx={idx} reduced={reduced} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
