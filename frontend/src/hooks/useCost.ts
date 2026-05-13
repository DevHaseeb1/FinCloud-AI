"use client";

import { useQuery } from "@tanstack/react-query";
import { costService } from "@/services/costService";
import { useDataMode } from "@/lib/mode";

export function useCostSummary() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["cost", "summary", mode],
    queryFn: () => costService.summary({ mode }),
  });
}

export function useCostTimeseries(params?: {
  start?: string;
  end?: string;
  service?: string;
  region?: string;
}) {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["cost", "timeseries", mode, params],
    queryFn: async () => {
      const data = await costService.timeseries({ ...params, mode });
      // Unwrap if nested in timeseries object
      return Array.isArray(data) ? data : data?.timeseries ?? [];
    },
  });
}

export function useServiceBreakdown(params?: { start?: string; end?: string }) {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["cost", "service-breakdown", mode, params],
    queryFn: async () => {
      const data = await costService.serviceBreakdown({ ...params, mode });
      // Unwrap if nested in breakdown object
      return Array.isArray(data) ? data : data?.breakdown ?? [];
    },
  });
}

export function useRegionBreakdown(params?: { start?: string; end?: string }) {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["cost", "region-breakdown", mode, params],
    queryFn: async () => {
      const data = await costService.regionBreakdown({ ...params, mode });
      // Unwrap if nested in breakdown object
      return Array.isArray(data) ? data : data?.breakdown ?? [];
    },
  });
}

