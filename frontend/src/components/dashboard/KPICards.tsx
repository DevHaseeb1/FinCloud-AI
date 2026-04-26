"use client";

import { TrendingDown, TrendingUp, Wallet } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCostSummary } from "@/hooks/useCost";
import { formatCurrency, formatPct } from "@/lib/format";

export function KPICards() {
  const q = useCostSummary();
  const currency = q.data?.currency || "USD";

  const change = q.data?.cost_change_pct;
  const changeUp = typeof change === "number" ? change >= 0 : undefined;
  const TrendIcon = changeUp ? TrendingUp : TrendingDown;

  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
          <Wallet className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          {q.isLoading ? (
            <Skeleton className="h-8 w-32" />
          ) : (
            <div className="text-2xl font-semibold">
              {formatCurrency(q.data?.total_cost, { currency })}
            </div>
          )}
          <p className="text-xs text-muted-foreground">Across selected time window</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Monthly Cost</CardTitle>
          <Wallet className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          {q.isLoading ? (
            <Skeleton className="h-8 w-32" />
          ) : (
            <div className="text-2xl font-semibold">
              {formatCurrency(q.data?.monthly_cost, { currency })}
            </div>
          )}
          <p className="text-xs text-muted-foreground">Current month burn</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Cost Change</CardTitle>
          <TrendIcon className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          {q.isLoading ? (
            <Skeleton className="h-8 w-24" />
          ) : (
            <div className="text-2xl font-semibold">{formatPct(change)}</div>
          )}
          <p className="text-xs text-muted-foreground">Vs previous period</p>
        </CardContent>
      </Card>
    </div>
  );
}

