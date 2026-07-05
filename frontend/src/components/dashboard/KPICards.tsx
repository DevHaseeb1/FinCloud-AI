"use client";

import * as React from "react";
import { TrendingDown, TrendingUp, Wallet, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Sparkline } from "@/components/charts/Sparkline";
import { useCostSummary, useCostTimeseries } from "@/hooks/useCost";
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
  sparkData,
  sparkColor,
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
  sparkData?: Array<Record<string, any>>;
  sparkColor?: string;
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
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      <Card
        className={cn(
          "group relative overflow-hidden border-border/50 bg-card shadow-sm transition-all duration-200",
          "hover:shadow-md hover:-translate-y-0.5",
          "border-l-[3px] border-l-transparent",
        )}
        style={{
          borderLeftColor: sparkColor || "var(--cyan)",
        }}
      >
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          <span className={iconColor}>{icon}</span>
        </CardHeader>
        <CardContent className="space-y-1.5">
          {isLoading ? (
            <Skeleton className="h-8 w-32" />
          ) : (
            <div className="text-2xl font-bold tracking-tight font-mono" aria-live="polite" aria-atomic="true">
              <span>
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
              <p className="text-xs text-muted-foreground">{subtitle}</p>
            ) : (
              subtitle
            )}
          </div>
          {sparkData && sparkData.length > 0 ? (
            <Sparkline data={sparkData} dataKey="cost" color={sparkColor || "var(--cyan)"} height={32} />
          ) : (
            <div className="h-8" />
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function DeltaBadge({ value, className }: { value?: number; className?: string }) {
  if (typeof value !== "number") return null;
  const isUp = value >= 0;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-0.5 rounded-full px-1.5 py-0.5 text-[10px] font-semibold font-mono",
        isUp
          ? "bg-red-500/10 text-red-600 dark:text-red-400"
          : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
        className,
      )}
    >
      {isUp ? <TrendingUp className="size-2.5" /> : <TrendingDown className="size-2.5" />}
      {isUp ? "+" : ""}{value.toFixed(1)}%
    </span>
  );
}

export function KPICards() {
  const costQ = useCostSummary();
  const timeseriesQ = useCostTimeseries();
  const recsQ = useRecommendations();
  const reduced = useReducedMotion();

  const currency = costQ.data?.currency || "USD";
  const change = costQ.data?.cost_change_pct;
  const changeUp = typeof change === "number" ? change >= 0 : undefined;
  const TrendIcon = changeUp ? TrendingUp : TrendingDown;

  const totalSavings = recsQ.data?.reduce((sum: number, r: Recommendation) => sum + (r.estimated_savings ?? 0), 0) ?? 0;

  const timeseriesData = timeseriesQ.data ?? [];
  const last7 = timeseriesData.slice(-7);

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
        sparkData={last7}
        sparkColor="var(--cyan)"
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
        sparkData={last7}
        sparkColor="var(--violet)"
      />
      <KpiCard
        title="Avg Daily Cost"
        icon={<TrendIcon className="size-4" />}
        iconColor={changeUp === true ? "text-ember" : changeUp === false ? "text-emerald-500" : "text-muted-foreground"}
        value={costQ.data?.average_daily_cost}
        formatFn={(v) => formatCurrency(v, { currency })}
        subtitle={
          <div className="flex items-center gap-2">
            <p className="text-xs text-muted-foreground">vs previous period</p>
            <DeltaBadge value={change} />
          </div>
        }
        index={2}
        isLoading={costQ.isLoading}
        reduced={reduced}
        sparkData={last7}
        sparkColor={changeUp === true ? "var(--ember)" : "var(--cyan)"}
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
        sparkColor="var(--emerald-500, oklch(0.65 0.15 160))"
      />
    </div>
  );
}
