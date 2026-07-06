"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { PieChart } from "@/components/charts/PieChart";
import { useRegionBreakdown } from "@/hooks/useCost";
import { formatCurrency } from "@/lib/format";
import { Globe } from "lucide-react";
import type { BreakdownItem } from "@/types/apiTypes";

export function RegionBreakdown() {
  const q = useRegionBreakdown();
  const currency = "USD";

  const totalCost = q.data?.reduce((sum: number, item: BreakdownItem) => sum + (item.cost ?? 0), 0) ?? 0;
  const topRegion = q.data?.[0];

  return (
    <Card className="relative overflow-hidden border-border/50 bg-card shadow-sm h-full">
      <CardHeader className="relative">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Globe className="size-4 text-violet" />
              Region Breakdown
            </CardTitle>
            <CardDescription>Cost distribution by AWS region</CardDescription>
          </div>
          {totalCost > 0 && (
            <div className="text-right">
              <div className="text-xs text-muted-foreground">Total</div>
              <div className="text-lg font-semibold font-mono">{formatCurrency(totalCost, { currency })}</div>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="relative">
        {q.isLoading ? (
          <Skeleton className="h-72 w-full rounded-lg" />
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load region breakdown.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No regional cost data yet.</div>
        ) : (
          <>
            <PieChart
              data={q.data?.slice(0, 10) ?? []}
              nameKey="name"
              valueKey="cost"
              valueFormatter={(v) => formatCurrency(v, { currency })}
            />
            {topRegion && (
              <div className="mt-4 pt-4 border-t border-border/50">
                <div className="text-xs font-medium text-muted-foreground">Primary Region</div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{topRegion.name}</span>
                  <span className="text-sm font-semibold font-mono">{formatCurrency(topRegion.cost, { currency })}</span>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
