"use client";

import * as React from "react";
import { KPICards } from "@/components/dashboard/KPICards";
import { CostOverview } from "@/components/dashboard/CostOverview";
import { ServiceBreakdown } from "@/components/dashboard/ServiceBreakdown";
import { RegionBreakdown } from "@/components/dashboard/RegionBreakdown";
import { AnomalyPanel } from "@/components/dashboard/AnomalyPanel";
import { ForecastPanel } from "@/components/dashboard/ForecastPanel";
import { RecommendationsPanel } from "@/components/dashboard/RecommendationsPanel";
import { DateRangePicker } from "@/components/filters/DateRangePicker";
import { useAuth } from "@/hooks/useAuth";
import { useQueryClient } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

function DashboardSkeleton() {
  return (
    <div className="space-y-8 pb-8">
      <div className="space-y-2">
        <Skeleton className="h-9 w-64" />
        <Skeleton className="h-4 w-96" />
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-xl border border-border/50 bg-card p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="size-4 rounded" />
            </div>
            <Skeleton className="h-9 w-32" />
            <Skeleton className="h-3 w-20" />
            <Skeleton className="h-12 w-full" />
          </div>
        ))}
      </div>
      <div className="rounded-xl border border-border/50 bg-card p-6 shadow-sm space-y-4">
        <Skeleton className="h-5 w-48" />
        <Skeleton className="h-72 w-full" />
      </div>
      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3 rounded-xl border border-border/50 bg-card p-6 shadow-sm space-y-4">
          <Skeleton className="h-5 w-48" />
          <Skeleton className="h-72 w-full" />
        </div>
        <div className="lg:col-span-2 rounded-xl border border-border/50 bg-card p-6 shadow-sm space-y-4">
          <Skeleton className="h-5 w-48" />
          <Skeleton className="h-72 w-full" />
        </div>
      </div>
    </div>
  );
}

export function DashboardPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [dateRange, setDateRange] = React.useState<{ from?: Date; to?: Date }>({});
  const [refreshing, setRefreshing] = React.useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await queryClient.invalidateQueries({ queryKey: ["cost"] });
    await queryClient.invalidateQueries({ queryKey: ["anomalies"] });
    await queryClient.invalidateQueries({ queryKey: ["forecast"] });
    await queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    setTimeout(() => setRefreshing(false), 600);
  };

  return (
    <div className="space-y-6 pb-8 overflow-x-hidden">
      {/* Decorative background — single page-level orb */}
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute -left-32 -top-32 size-96 rounded-full bg-primary/5 blur-3xl" />
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome{user ? `, ` : ""}
            {user && (
              <span className="bg-gradient-to-r from-cyan to-violet bg-clip-text text-transparent">
                {user.name}
              </span>
            )}
          </h1>
          <p className="text-sm text-muted-foreground">
            Here&apos;s what&apos;s happening with your cloud costs.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <DateRangePicker value={dateRange} onChange={setDateRange} />
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`size-4 ${refreshing ? "animate-spin" : ""}`} />
            <span className="hidden sm:inline ml-1">Refresh</span>
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <KPICards />

      {/* Section: Overview */}
      <div>
        <p className="mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground/60">
          Overview
        </p>
        <CostOverview />
      </div>

      {/* Section: Breakdown */}
      <div>
        <p className="mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground/60">
          Breakdown
        </p>
        <div className="grid gap-6 lg:grid-cols-5">
          <div className="lg:col-span-3">
            <ServiceBreakdown />
          </div>
          <div className="lg:col-span-2">
            <RegionBreakdown />
          </div>
        </div>
      </div>

      {/* Section: Analysis */}
      <div>
        <p className="mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground/60">
          Analysis
        </p>
        <div className="grid gap-6 lg:grid-cols-5">
          <div className="lg:col-span-3">
            <AnomalyPanel />
          </div>
          <div className="lg:col-span-2">
            <ForecastPanel />
          </div>
        </div>
      </div>

      {/* Recommendations — full width */}
      <RecommendationsPanel />
    </div>
  );
}
