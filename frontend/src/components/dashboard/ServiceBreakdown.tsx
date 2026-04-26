"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { PieChart } from "@/components/charts/PieChart";
import { useServiceBreakdown } from "@/hooks/useCost";
import { formatCurrency } from "@/lib/format";

export function ServiceBreakdown() {
  const q = useServiceBreakdown();
  const currency = "USD";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Service Breakdown</CardTitle>
      </CardHeader>
      <CardContent>
        {q.isLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load service breakdown.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No service cost data yet.</div>
        ) : (
          <PieChart
            data={q.data?.slice(0, 8) ?? []}
            nameKey="name"
            valueKey="cost"
            valueFormatter={(v) => formatCurrency(v, { currency })}
          />
        )}
      </CardContent>
    </Card>
  );
}

