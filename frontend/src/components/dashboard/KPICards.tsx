"use client";

import { TrendingDown, TrendingUp, Wallet, Zap, TrendingUp as SavingsIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCostSummary } from "@/hooks/useCost";
import { useRecommendations } from "@/hooks/useRecommendations";
import { formatCurrency, formatPct } from "@/lib/format";
import type { Recommendation } from "@/types/apiTypes";

export function KPICards() {
  const costQ = useCostSummary();
  const recsQ = useRecommendations();
  
  const currency = costQ.data?.currency || "USD";
  const change = costQ.data?.cost_change_pct;
  const changeUp = typeof change === "number" ? change >= 0 : undefined;
  const TrendIcon = changeUp ? TrendingUp : TrendingDown;

  // Calculate total potential savings from recommendations
  const totalSavings = recsQ.data?.reduce((sum: number, r: Recommendation) => sum + (r.estimated_savings ?? 0), 0) ?? 0;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card className="relative overflow-hidden border-border/50 bg-card/50 backdrop-blur-sm">
        <div className="absolute -right-12 -top-12 size-32 rounded-full bg-primary/5" />
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
          <Wallet className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent className="relative">
          {costQ.isLoading ? (
            <Skeleton className="h-8 w-32" />
          ) : (
            <div className="text-2xl font-bold tracking-tight">
              {formatCurrency(costQ.data?.total_cost, { currency })}
            </div>
          )}
          <p className="text-xs text-muted-foreground mt-1">Across selected time window</p>
        </CardContent>
      </Card>

      <Card className="relative overflow-hidden border-border/50 bg-card/50 backdrop-blur-sm">
        <div className="absolute -right-12 -top-12 size-32 rounded-full bg-blue-500/5" />
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Monthly Cost</CardTitle>
          <Zap className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent className="relative">
          {costQ.isLoading ? (
            <Skeleton className="h-8 w-32" />
          ) : (
            <div className="text-2xl font-bold tracking-tight">
              {formatCurrency(costQ.data?.monthly_cost, { currency })}
            </div>
          )}
          <p className="text-xs text-muted-foreground mt-1">Current month burn</p>
        </CardContent>
      </Card>

      <Card className="relative overflow-hidden border-border/50 bg-card/50 backdrop-blur-sm">
        <div className="absolute -right-12 -top-12 size-32 rounded-full bg-green-500/5" />
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Avg Daily Cost</CardTitle>
          <TrendIcon className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent className="relative">
          {costQ.isLoading ? (
            <Skeleton className="h-8 w-32" />
          ) : (
            <div className="text-2xl font-bold tracking-tight">
              {formatCurrency(costQ.data?.average_daily_cost, { currency })}
            </div>
          )}
          <p className="text-xs text-muted-foreground mt-1">
            {formatPct(change)} vs previous period
          </p>
        </CardContent>
      </Card>

      <Card className="relative overflow-hidden border-border/50 bg-card/50 backdrop-blur-sm">
        <div className="absolute -right-12 -top-12 size-32 rounded-full bg-emerald-500/5" />
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Potential Savings</CardTitle>
          <SavingsIcon className="size-4 text-emerald-500/70" />
        </CardHeader>
        <CardContent className="relative">
          {recsQ.isLoading ? (
            <Skeleton className="h-8 w-32" />
          ) : (
            <div className="text-2xl font-bold tracking-tight text-emerald-600 dark:text-emerald-400">
              {formatCurrency(totalSavings, { currency })}
            </div>
          )}
          <p className="text-xs text-muted-foreground mt-1">From {recsQ.data?.length ?? 0} recommendations</p>
        </CardContent>
      </Card>
    </div>
  );
}

