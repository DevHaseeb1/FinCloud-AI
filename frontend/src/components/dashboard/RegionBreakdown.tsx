"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { BarChart } from "@/components/charts/BarChart";
import { useRegionBreakdown } from "@/hooks/useCost";
import { formatCurrency } from "@/lib/format";

export function RegionBreakdown() {
  const q = useRegionBreakdown();
  const currency = "USD";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Region Cost</CardTitle>
      </CardHeader>
      <CardContent>
        {q.isLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load region breakdown.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No regional cost data yet.</div>
        ) : (
          <BarChart
            data={q.data?.slice(0, 10) ?? []}
            xKey="name"
            yKey="cost"
            yFormatter={(v) => formatCurrency(v, { currency })}
          />
        )}
      </CardContent>
    </Card>
  );
}

