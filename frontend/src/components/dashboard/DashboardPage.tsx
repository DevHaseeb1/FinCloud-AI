"use client";

import * as React from "react";
import { KPICards } from "@/components/dashboard/KPICards";
import { CostOverview } from "@/components/dashboard/CostOverview";
import { ServiceBreakdown } from "@/components/dashboard/ServiceBreakdown";
import { RegionBreakdown } from "@/components/dashboard/RegionBreakdown";
import { AnomalyPanel } from "@/components/dashboard/AnomalyPanel";
import { ForecastPanel } from "@/components/dashboard/ForecastPanel";
import { RecommendationsPanel } from "@/components/dashboard/RecommendationsPanel";
import { useAuth } from "@/hooks/useAuth";

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-8 pb-8 overflow-x-hidden">
      {/* Decorative background */}
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute -left-32 -top-32 size-96 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute -bottom-32 -right-32 size-96 rounded-full bg-accent/5 blur-3xl" />
      </div>

      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">
          Welcome{user ? `, ${user.name}` : ""}
        </h1>
        <p className="text-muted-foreground">
          Real-time cloud cost analytics, anomaly detection, forecasting, and optimization recommendations.
        </p>
      </div>

      {/* KPI Cards */}
      <div>
        <KPICards />
      </div>

      {/* Main Content Grid */}
      <div className="space-y-6">
        {/* Cost Overview - Full Width */}
        <CostOverview />

        {/* Service & Region Breakdown */}
        <div className="grid gap-6 lg:grid-cols-2">
          <ServiceBreakdown />
          <RegionBreakdown />
        </div>

        {/* Anomalies & Forecast */}
        <div className="grid gap-6 lg:grid-cols-2">
          <AnomalyPanel />
          <ForecastPanel />
        </div>

        {/* Recommendations */}
        <RecommendationsPanel />
      </div>
    </div>
  );
}

