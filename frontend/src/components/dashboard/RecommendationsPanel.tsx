"use client";

import { Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useRecommendations } from "@/hooks/useRecommendations";
import { formatCurrency } from "@/lib/format";

function priorityVariant(priority?: string) {
  if (priority === "high") return "destructive";
  if (priority === "medium") return "secondary";
  return "outline";
}

export function RecommendationsPanel() {
  const q = useRecommendations();
  const currency = "USD";

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="size-4 text-muted-foreground" /> Recommendations
        </CardTitle>
        <Badge variant="outline">{q.data?.length ?? 0}</Badge>
      </CardHeader>
      <CardContent className="space-y-3">
        {q.isLoading ? (
          <>
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </>
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load recommendations.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No recommendations yet.</div>
        ) : (
          <div className="grid gap-2">
            {q.data?.slice(0, 5).map((r, idx) => (
              <div key={String(r.id ?? idx)} className="rounded-md border p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium">{r.title ?? "Optimization"}</div>
                    <div className="truncate text-xs text-muted-foreground">
                      {r.category ?? "Cost"} {r.description ? `• ${r.description}` : ""}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {typeof r.estimated_savings === "number" ? (
                      <Badge variant="outline">
                        {formatCurrency(r.estimated_savings, { currency })} / mo
                      </Badge>
                    ) : null}
                    <Badge variant={priorityVariant(r.priority) as any}>
                      {r.priority ?? "low"}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

