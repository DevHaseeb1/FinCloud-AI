"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ForecastAreaChart } from "@/components/charts/ForecastAreaChart";
import { useForecastNext30 } from "@/hooks/useForecast";
import { formatCurrency } from "@/lib/format";

export function ForecastPanel() {
  const q = useForecastNext30();
  const currency = "USD";

  return (
    <Card>
      <CardHeader>
        <CardTitle>30-Day Forecast</CardTitle>
      </CardHeader>
      <CardContent>
        {q.isLoading ? (
          <Skeleton className="h-72 w-full" />
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load forecast.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No forecast available yet.</div>
        ) : (
          <ForecastAreaChart
            data={q.data ?? []}
            xKey="date"
            actualKey="actual"
            predictedKey="predicted"
            lowerKey="lower"
            upperKey="upper"
            yFormatter={(v) => formatCurrency(v, { currency })}
          />
        )}
      </CardContent>
    </Card>
  );
}

