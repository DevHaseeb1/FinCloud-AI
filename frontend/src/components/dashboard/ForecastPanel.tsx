"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ForecastAreaChart } from "@/components/charts/ForecastAreaChart";
import { useForecastNext30 } from "@/hooks/useForecast";
import { formatCurrency } from "@/lib/format";
import type { ForecastPoint } from "@/types/apiTypes";
import { TrendingUp } from "lucide-react";

export function ForecastPanel() {
  const q = useForecastNext30();
  const currency = "USD";

  // Calculate projected totals
  const totalPredicted = q.data?.reduce((sum: number, f: ForecastPoint) => sum + (f.predicted ?? 0), 0) ?? 0;
  const avgPredicted = q.data && q.data.length > 0 ? totalPredicted / q.data.length : 0;

  return (
    <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-card/50 via-card/30 to-card/50 backdrop-blur-sm">
      <div className="absolute -right-32 -top-32 size-64 rounded-full bg-cyan-500/5 blur-3xl" />
      <CardHeader className="relative">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="size-4" />
              30-Day Forecast
            </CardTitle>
            <CardDescription>Projected cloud costs with confidence bounds</CardDescription>
          </div>
          {q.data && q.data.length > 0 && (
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Projected Total</div>
              <div className="text-lg font-semibold">{formatCurrency(totalPredicted, { currency })}</div>
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
          <>
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
                  <div className="text-xs font-medium text-muted-foreground">Average Daily Cost</div>
                  <div className="text-lg font-semibold">{formatCurrency(avgPredicted, { currency })}</div>
                </div>
                <div>
                  <div className="text-xs font-medium text-muted-foreground">Forecast Records</div>
                  <div className="text-lg font-semibold">{q.data?.length ?? 0} days</div>
                </div>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

