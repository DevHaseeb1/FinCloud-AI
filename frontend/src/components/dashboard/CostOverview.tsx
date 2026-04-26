"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { LineChart } from "@/components/charts/LineChart";
import { useCostTimeseries } from "@/hooks/useCost";
import { formatCurrency } from "@/lib/format";

export function CostOverview() {
  const q = useCostTimeseries();
  const currency = "USD";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Cost Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        {q.isLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load cost timeseries.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No cost data available yet.</div>
        ) : (
          <LineChart
            data={q.data ?? []}
            xKey="date"
            yKey="cost"
            yFormatter={(v) => formatCurrency(v, { currency })}
          />
        )}
      </CardContent>
    </Card>
  );
}

