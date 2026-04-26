"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useRecommendations } from "@/hooks/useRecommendations";
import { formatCurrency } from "@/lib/format";

function priorityVariant(priority?: string) {
  if (priority === "high") return "destructive";
  if (priority === "medium") return "secondary";
  return "outline";
}

export default function RecommendationsPage() {
  const q = useRecommendations();
  const currency = "USD";

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold tracking-tight">Recommendations</h1>
        <p className="text-sm text-muted-foreground">
          Prioritized optimizations with estimated savings.
        </p>
      </div>

      {q.isLoading ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
        </div>
      ) : q.isError ? (
        <div className="text-sm text-destructive">Failed to load recommendations.</div>
      ) : (q.data?.length ?? 0) === 0 ? (
        <div className="text-sm text-muted-foreground">No recommendations yet.</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {q.data?.map((r, idx) => (
            <Card key={String(r.id ?? idx)}>
              <CardHeader className="flex flex-row items-start justify-between gap-3">
                <div className="min-w-0">
                  <CardTitle className="truncate text-base">{r.title ?? "Optimization"}</CardTitle>
                  <div className="mt-1 text-sm text-muted-foreground line-clamp-2">
                    {r.description ?? "No description provided."}
                  </div>
                </div>
                <Badge variant={priorityVariant(r.priority) as any}>{r.priority ?? "low"}</Badge>
              </CardHeader>
              <CardContent className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">{r.category ?? "Cost"}</div>
                {typeof r.estimated_savings === "number" ? (
                  <Badge variant="outline">
                    {formatCurrency(r.estimated_savings, { currency })} / mo
                  </Badge>
                ) : (
                  <Badge variant="outline">Savings n/a</Badge>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

