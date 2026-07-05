"use client";

import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ForecastAreaChart } from "@/components/charts/ForecastAreaChart";
import { useForecastNext30 } from "@/hooks/useForecast";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { formatCurrency } from "@/lib/format";
import type { ForecastPoint } from "@/types/apiTypes";
import { TrendingUp } from "lucide-react";

export function ForecastPanel() {
  const q = useForecastNext30();
  const reduced = useReducedMotion();
  const currency = "USD";
  const [showData, setShowData] = React.useState(false);

  const totalPredicted = q.data?.reduce((sum: number, f: ForecastPoint) => sum + (f.predicted ?? 0), 0) ?? 0;
  const avgPredicted = q.data && q.data.length > 0 ? totalPredicted / q.data.length : 0;

  React.useEffect(() => {
    if (q.isSuccess) {
      const timer = setTimeout(() => setShowData(true), reduced ? 0 : 300);
      return () => clearTimeout(timer);
    }
    setShowData(false);
  }, [q.isSuccess, q.data, reduced]);

  return (
    <Card className="relative overflow-hidden border-border/50 bg-card shadow-sm h-full">
      <CardHeader className="relative">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="size-4 text-cyan" />
              30-Day Forecast
            </CardTitle>
            <CardDescription>Projected cloud costs with confidence bounds</CardDescription>
          </div>
          {q.data && q.data.length > 0 && (
            <div className="text-right">
              <div className="text-xs text-muted-foreground">Projected Total</div>
              <div className="text-lg font-semibold font-mono">{formatCurrency(totalPredicted, { currency })}</div>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="relative">
        {q.isLoading ? (
          <Skeleton className="h-72 w-full rounded-lg" />
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load forecast.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No forecast available yet.</div>
        ) : (
          <div
            className="transition-all duration-300"
            style={{
              opacity: showData ? 1 : 0,
              transitionTimingFunction: "var(--ease-out-expo)",
            }}
          >
            <ForecastAreaChart
              data={q.data ?? []}
              xKey="date"
              actualKey="actual"
              predictedKey="predicted"
              lowerKey="lower"
              upperKey="upper"
              yFormatter={(v) => formatCurrency(v, { currency })}
            />
            <div className="mt-4 pt-4 border-t border-border/50">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs font-medium text-muted-foreground">Avg Daily Cost</div>
                  <div className="text-lg font-semibold font-mono">{formatCurrency(avgPredicted, { currency })}</div>
                </div>
                <div>
                  <div className="text-xs font-medium text-muted-foreground">Forecast Period</div>
                  <div className="text-lg font-semibold font-mono">{q.data?.length ?? 0} days</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
