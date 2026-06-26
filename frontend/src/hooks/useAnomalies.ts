"use client";

import { useQuery } from "@tanstack/react-query";
import { anomalyService } from "@/services/anomalyService";
import { useDataMode } from "@/lib/mode";
import type { AnomalyFilterParams } from "@/services/anomalyService";

export function useAnomalies(params?: AnomalyFilterParams) {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["anomalies", "list", mode, params],
    queryFn: async () => {
      const data = await anomalyService.list({ ...params, mode });
      return data;
    },
  });
}

export function useLatestAnomalies() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["anomalies", "latest", mode],
    queryFn: async () => {
      const data = await anomalyService.latest({ mode });
      return data;
    },
  });
}
