"use client";

import * as React from "react";
import { Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useServiceBreakdown } from "@/hooks/useCost";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { staggerDelay } from "@/lib/animations";
import { formatCurrency, formatPct } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { BreakdownItem } from "@/types/apiTypes";

function Bar({ item, maxCost, currency, index, reduced }: { item: BreakdownItem; maxCost: number; currency: string; index: number; reduced: boolean }) {
  const [visible, setVisible] = React.useState(false);
  const pct = maxCost > 0 ? (item.cost / maxCost) * 100 : 0;

  React.useEffect(() => {
    const timer = setTimeout(() => setVisible(true), staggerDelay(index, 80));
    return () => clearTimeout(timer);
  }, [index]);

  return (
    <div
      className={cn(
        "transition-all duration-600",
        !visible && "opacity-0",
        visible && "opacity-100",
      )}
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      <div className="flex items-center gap-3">
        <span className="w-24 shrink-0 truncate text-sm font-medium text-right">{item.name}</span>
        <div className="flex-1 h-7 rounded-md bg-muted/50 overflow-hidden">
          <div
            className={cn(
              "h-full rounded-md transition-all duration-600 hover:brightness-110",
            )}
            style={{
              width: visible ? `${pct}%` : "0%",
              transitionTimingFunction: "var(--ease-out-expo)",
              transitionDelay: visible ? `${staggerDelay(index, 80)}ms` : "0ms",
              background: "linear-gradient(90deg, var(--cyan), var(--violet))",
            }}
          />
        </div>
        <span className="w-28 shrink-0 text-sm font-mono font-semibold text-right">
          {formatCurrency(item.cost, { currency })}
        </span>
      </div>
    </div>
  );
}

export function ServiceBreakdown() {
  const q = useServiceBreakdown();
  const reduced = useReducedMotion();
  const currency = "USD";

  const data = q.data?.slice(0, 8) ?? [];
  const totalCost = data.reduce((sum: number, item: BreakdownItem) => sum + (item.cost ?? 0), 0);
  const maxCost = data.reduce((max: number, item: BreakdownItem) => Math.max(max, item.cost ?? 0), 0);
  const topService = data[0];

  return (
    <Card className="relative overflow-hidden border-border/50 bg-surface/80 backdrop-blur-sm">
      <div className="absolute -right-32 -top-32 size-64 rounded-full bg-cyan/5 blur-3xl pointer-events-none" />
      <CardHeader className="relative">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Activity className="size-4 text-cyan" />
              Service Breakdown
            </CardTitle>
            <CardDescription>Cost distribution by AWS service</CardDescription>
          </div>
          {totalCost > 0 && (
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Total</div>
              <div className="text-lg font-semibold font-mono">{formatCurrency(totalCost, { currency })}</div>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="relative">
        {q.isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-7 w-full" />
            <Skeleton className="h-7 w-3/4" />
            <Skeleton className="h-7 w-5/6" />
            <Skeleton className="h-7 w-2/3" />
          </div>
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load service breakdown.</div>
        ) : data.length === 0 ? (
          <div className="text-sm text-muted-foreground">No service cost data yet.</div>
        ) : (
          <div className="space-y-2.5">
            {data.map((item: BreakdownItem, idx: number) => (
              <Bar key={item.name} item={item} maxCost={maxCost} currency={currency} index={idx} reduced={reduced} />
            ))}
            {topService && (
              <div className="mt-4 pt-4 border-t border-border/50">
                <div className="text-xs font-medium text-muted-foreground">Top Service</div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{topService.name}</span>
                  <span className="text-sm font-semibold font-mono">{formatCurrency(topService.cost, { currency })}</span>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
