"use client";

import * as React from "react";
import { TrendingDown, TrendingUp, Wallet, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCostSummary } from "@/hooks/useCost";
import { useRecommendations } from "@/hooks/useRecommendations";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { useCountUp, staggerDelay } from "@/lib/animations";
import { cn } from "@/lib/utils";
import { formatCurrency, formatPct } from "@/lib/format";
import type { Recommendation } from "@/types/apiTypes";

function KpiCard({
  title,
  icon,
  iconColor,
  value,
  subtitle,
  formatFn,
  index,
  isLoading,
  reduced,
}: {
  title: string;
  icon: React.ReactNode;
  iconColor: string;
  value?: number;
  subtitle: string | React.ReactNode;
  formatFn?: (v: number) => string;
  index: number;
  isLoading: boolean;
  reduced: boolean;
}) {
  const [visible, setVisible] = React.useState(false);
  const counted = useCountUp(value ?? 0, 800, reduced || isLoading);

  React.useEffect(() => {
    const timer = setTimeout(() => setVisible(true), staggerDelay(index, 60));
    return () => clearTimeout(timer);
  }, [index]);

  return (
    <div
      className={cn(
        "transition-all duration-320",
        !visible && "opacity-0 translate-y-4",
        visible && "opacity-100 translate-y-0",
      )}
      style={{ transitionTimingFunction: "var(--ease-out-expo)", transitionDelay: visible ? "0ms" : "0ms" }}
    >
      <Card className="relative overflow-hidden border-border/50 bg-surface/80 backdrop-blur-sm">
        <div
          className="absolute inset-[-1px] rounded-[13px] pointer-events-none"
          style={{
            background: "conic-gradient(from var(--border-angle, 0deg), #00D4FF 0%, #7C3AED 40%, #00D4FF 80%, transparent 100%)",
            animation: reduced ? "none" : "gradient-border-spin 3s linear infinite",
            WebkitMask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
            WebkitMaskComposite: "xor",
            mask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
            maskComposite: "exclude",
            padding: "1px",
          }}
        />
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          <span className={iconColor}>{icon}</span>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-8 w-32" />
          ) : (
            <div className="text-2xl font-bold tracking-tight font-mono" aria-live="polite" aria-atomic="true">
              <span
                className={cn(
                  !reduced && "bg-[length:200%_100%] bg-clip-text text-transparent bg-gradient-to-r from-foreground via-cyan to-foreground",
                  !reduced && "animate-value-shimmer",
                )}
                style={{
                  backgroundImage: reduced ? "none" : undefined,
                }}
              >
                {formatFn ? formatFn(counted) : counted}
              </span>
            </div>
          )}
          <div
            className={cn(
              "transition-all duration-400",
              !visible && "opacity-0 -translate-y-1",
              visible && "opacity-100 translate-y-0",
            )}
            style={{ transitionTimingFunction: "var(--ease-out-expo)", transitionDelay: "400ms" }}
          >
            {typeof subtitle === "string" ? (
              <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
            ) : (
              subtitle
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export function KPICards() {
  const costQ = useCostSummary();
  const recsQ = useRecommendations();
  const reduced = useReducedMotion();

  const currency = costQ.data?.currency || "USD";
  const change = costQ.data?.cost_change_pct;
  const changeUp = typeof change === "number" ? change >= 0 : undefined;
  const TrendIcon = changeUp ? TrendingUp : TrendingDown;

  const totalSavings = recsQ.data?.reduce((sum: number, r: Recommendation) => sum + (r.estimated_savings ?? 0), 0) ?? 0;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <KpiCard
        title="Total Cost"
        icon={<Wallet className="size-4" />}
        iconColor="text-cyan"
        value={costQ.data?.total_cost}
        formatFn={(v) => formatCurrency(v, { currency })}
        subtitle="Across selected time window"
        index={0}
        isLoading={costQ.isLoading}
        reduced={reduced}
      />
      <KpiCard
        title="Monthly Cost"
        icon={<Zap className="size-4" />}
        iconColor="text-violet"
        value={costQ.data?.monthly_cost}
        formatFn={(v) => formatCurrency(v, { currency })}
        subtitle="Current month burn"
        index={1}
        isLoading={costQ.isLoading}
        reduced={reduced}
      />
      <KpiCard
        title="Avg Daily Cost"
        icon={<TrendIcon className="size-4" />}
        iconColor={changeUp === true ? "text-ember" : changeUp === false ? "text-green-500" : "text-muted-foreground"}
        value={costQ.data?.average_daily_cost}
        formatFn={(v) => formatCurrency(v, { currency })}
        subtitle={
          <p className={cn("text-xs mt-1", changeUp === true ? "text-ember" : changeUp === false ? "text-green-500" : "text-muted-foreground")}>
            {formatPct(change)} vs previous period
          </p>
        }
        index={2}
        isLoading={costQ.isLoading}
        reduced={reduced}
      />
      <KpiCard
        title="Potential Savings"
        icon={<TrendingUp className="size-4" />}
        iconColor="text-emerald-500"
        value={totalSavings}
        formatFn={(v) => formatCurrency(v, { currency })}
        subtitle={`From ${recsQ.data?.length ?? 0} recommendations`}
        index={3}
        isLoading={recsQ.isLoading}
        reduced={reduced}
      />
    </div>
  );
}
