"use client";

import { KPICards } from "@/components/dashboard/KPICards";
import { CostOverview } from "@/components/dashboard/CostOverview";
import { ServiceBreakdown } from "@/components/dashboard/ServiceBreakdown";
import { RegionBreakdown } from "@/components/dashboard/RegionBreakdown";
import { AnomalyPanel } from "@/components/dashboard/AnomalyPanel";
import { ForecastPanel } from "@/components/dashboard/ForecastPanel";
import { RecommendationsPanel } from "@/components/dashboard/RecommendationsPanel";
import { Separator } from "@/components/ui/separator";

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Cloud cost analytics, anomaly detection, forecasting, and recommendations.
        </p>
      </div>

      <KPICards />

      <Separator />

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <CostOverview />
        </div>
        <ServiceBreakdown />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <RegionBreakdown />
        <AnomalyPanel />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ForecastPanel />
        <RecommendationsPanel />
      </div>
    </div>
  );
}

