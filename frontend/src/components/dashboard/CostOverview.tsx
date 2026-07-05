"use client";

import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { LineChart } from "@/components/charts/LineChart";
import { useCostTimeseries } from "@/hooks/useCost";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { formatCurrency } from "@/lib/format";
import type { CostTimeseriesPoint } from "@/types/apiTypes";
import { TrendingUp, TrendingDown } from "lucide-react";

export function CostOverview() {
  const q = useCostTimeseries();
  const reduced = useReducedMotion();
  const currency = "USD";
  const [showData, setShowData] = React.useState(false);

  const data = q.data ?? [];
  const latest = data[data.length - 1];
  const previous = data[data.length - 2];
  const trendUp = latest && previous && latest.cost > previous.cost;

  const avgCost = data.length > 0 ? data.reduce((sum: number, d: CostTimeseriesPoint) => sum + d.cost, 0) / data.length : 0;
  const maxCost = data.length > 0 ? Math.max(...data.map((d: CostTimeseriesPoint) => d.cost)) : 0;
  const minCost = data.length > 0 ? Math.min(...data.map((d: CostTimeseriesPoint) => d.cost)) : 0;

  React.useEffect(() => {
    if (q.isSuccess) {
      const timer = setTimeout(() => setShowData(true), reduced ? 0 : 150);
      return () => clearTimeout(timer);
    }
    setShowData(false);
  }, [q.isSuccess, q.data, reduced]);

  return (
    <Card className="relative overflow-hidden border-border/50 bg-card shadow-sm">
      <CardHeader className="relative">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <span>Daily Cost Trend</span>
              {trendUp !== undefined && (
                trendUp
                  ? <TrendingUp className="size-4 text-red-500/70" />
                  : <TrendingDown className="size-4 text-emerald-500/70" />
              )}
            </CardTitle>
            <CardDescription>Daily cloud spending over time</CardDescription>
          </div>
          {data.length > 0 && (
            <div className="text-right">
              <div className="text-xs text-muted-foreground">Average</div>
              <div className="text-lg font-semibold font-mono">{formatCurrency(avgCost, { currency })}</div>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="relative">
        {q.isLoading ? (
          <Skeleton className="h-72 w-full rounded-lg" />
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load cost timeseries.</div>
        ) : (data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No cost data available yet.</div>
        ) : (
          <div
            className="transition-all duration-300"
            style={{
              opacity: showData ? 1 : 0,
              transitionTimingFunction: "var(--ease-out-expo)",
            }}
          >
            <LineChart
              data={q.data ?? []}
              xKey="date"
              yKey="cost"
              yFormatter={(v) => formatCurrency(v, { currency })}
            />
            <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t border-border/50">
              <div>
                <div className="text-xs font-medium text-muted-foreground">Max Cost</div>
                <div className="text-lg font-semibold font-mono">{formatCurrency(maxCost, { currency })}</div>
              </div>
              <div>
                <div className="text-xs font-medium text-muted-foreground">Average Cost</div>
                <div className="text-lg font-semibold font-mono">{formatCurrency(avgCost, { currency })}</div>
              </div>
              <div>
                <div className="text-xs font-medium text-muted-foreground">Min Cost</div>
                <div className="text-lg font-semibold font-mono">{formatCurrency(minCost, { currency })}</div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
