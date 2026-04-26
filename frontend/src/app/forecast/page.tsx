"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ForecastAreaChart } from "@/components/charts/ForecastAreaChart";
import { useForecast } from "@/hooks/useForecast";
import { formatCurrency } from "@/lib/format";

export default function ForecastPage() {
  const q = useForecast();
  const currency = "USD";

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold tracking-tight">Forecast</h1>
        <p className="text-sm text-muted-foreground">
          Historical costs with predicted trajectory and confidence interval (when provided).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Historical + Predicted</CardTitle>
        </CardHeader>
        <CardContent>
          {q.isLoading ? (
            <Skeleton className="h-72 w-full" />
          ) : q.isError ? (
            <div className="text-sm text-destructive">Failed to load forecast.</div>
          ) : (q.data?.length ?? 0) === 0 ? (
            <div className="text-sm text-muted-foreground">No forecast data available.</div>
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
    </div>
  );
}

