import { getData } from "@/services/api";
import type { BreakdownItem, CostSummary, CostTimeseriesPoint } from "@/types/apiTypes";

export const costService = {
  summary: (opts?: { start?: string; end?: string; mode?: string }) =>
    getData<CostSummary>("/cost/summary", { params: opts }),

  timeseries: (opts?: { start?: string; end?: string; service?: string; region?: string; mode?: string }) =>
    getData<CostTimeseriesPoint[] | { timeseries: CostTimeseriesPoint[] }>("/cost/timeseries", { params: opts }),

  serviceBreakdown: (opts?: { start?: string; end?: string; mode?: string }) =>
    getData<BreakdownItem[] | { breakdown: BreakdownItem[] }>("/cost/service-breakdown", { params: opts }),

  regionBreakdown: (opts?: { start?: string; end?: string; mode?: string }) =>
    getData<BreakdownItem[] | { breakdown: BreakdownItem[] }>("/cost/region-breakdown", { params: opts }),
};

