"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { LineChart } from "@/components/charts/LineChart";
import { useCostTimeseries } from "@/hooks/useCost";
import { formatCurrency } from "@/lib/format";
import type { CostTimeseriesPoint } from "@/types/apiTypes";
import { TrendingUp } from "lucide-react";

export function CostOverview() {
  const q = useCostTimeseries();
  const currency = "USD";

  // Calculate trend indicators
  const data = q.data ?? [];
  const latest = data[data.length - 1];
  const previous = data[data.length - 2];
  const trendUp = latest && previous && latest.cost > previous.cost;

  const avgCost = data.length > 0 ? data.reduce((sum: number, d: CostTimeseriesPoint) => sum + d.cost, 0) / data.length : 0;
  const maxCost = data.length > 0 ? Math.max(...data.map((d: CostTimeseriesPoint) => d.cost)) : 0;
  const minCost = data.length > 0 ? Math.min(...data.map((d: CostTimeseriesPoint) => d.cost)) : 0;

  return (
    <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-card/50 via-card/30 to-card/50 backdrop-blur-sm">
      <div className="absolute -right-32 -top-32 size-64 rounded-full bg-primary/5 blur-3xl" />
      <CardHeader className="relative">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <span>Daily Cost Trend</span>
              {trendUp && <TrendingUp className="size-4 text-red-500/70" />}
            </CardTitle>
            <CardDescription>Last 30 days of cloud spending</CardDescription>
          </div>
          {data.length > 0 && (
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Average</div>
              <div className="text-lg font-semibold">{formatCurrency(avgCost, { currency })}</div>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="relative">
        {q.isLoading ? (
          <Skeleton className="h-64 w-full rounded-lg" />
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load cost timeseries.</div>
        ) : (data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No cost data available yet.</div>
        ) : (
          <>
            <LineChart
              data={q.data ?? []}
              xKey="date"
              yKey="cost"
              yFormatter={(v) => formatCurrency(v, { currency })}
            />
            <div className="mt-6 grid grid-cols-3 gap-4 pt-6 border-t border-border/50">
              <div>
                <div className="text-xs font-medium text-muted-foreground">Max Cost</div>
                <div className="text-lg font-semibold">{formatCurrency(maxCost, { currency })}</div>
              </div>
              <div>
                <div className="text-xs font-medium text-muted-foreground">Average Cost</div>
                <div className="text-lg font-semibold">{formatCurrency(avgCost, { currency })}</div>
              </div>
              <div>
                <div className="text-xs font-medium text-muted-foreground">Min Cost</div>
                <div className="text-lg font-semibold">{formatCurrency(minCost, { currency })}</div>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

