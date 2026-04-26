"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAnomalies } from "@/hooks/useAnomalies";

function riskBadge(score?: number) {
  if (typeof score !== "number") return <Badge variant="outline">n/a</Badge>;
  if (score >= 0.85) return <Badge variant="destructive">High</Badge>;
  if (score >= 0.6) return <Badge variant="secondary">Medium</Badge>;
  return <Badge variant="outline">Low</Badge>;
}

export default function AnomaliesPage() {
  const q = useAnomalies();

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold tracking-tight">Anomalies</h1>
        <p className="text-sm text-muted-foreground">
          Review detected anomalies and prioritize high-risk spikes.
        </p>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Detected Anomalies</CardTitle>
          <Badge variant="outline">{q.data?.length ?? 0}</Badge>
        </CardHeader>
        <CardContent>
          {q.isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : q.isError ? (
            <div className="text-sm text-destructive">Failed to load anomalies.</div>
          ) : (q.data?.length ?? 0) === 0 ? (
            <div className="text-sm text-muted-foreground">No anomalies detected.</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Risk</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead>Service</TableHead>
                  <TableHead>Region</TableHead>
                  <TableHead>Timestamp</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {q.data?.map((a, idx) => (
                  <TableRow key={String(a.id ?? idx)}>
                    <TableCell>{riskBadge(a.anomaly_score)}</TableCell>
                    <TableCell className="font-mono text-xs">
                      {typeof a.anomaly_score === "number" ? a.anomaly_score.toFixed(3) : "—"}
                    </TableCell>
                    <TableCell>{a.service ?? "—"}</TableCell>
                    <TableCell>{a.region ?? "—"}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {a.timestamp ?? "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

