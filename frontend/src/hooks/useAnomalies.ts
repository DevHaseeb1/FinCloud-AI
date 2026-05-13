"use client";

import { useQuery } from "@tanstack/react-query";
import { anomalyService } from "@/services/anomalyService";
import { useDataMode } from "@/lib/mode";

export function useAnomalies(params?: {
  start?: string;
  end?: string;
  service?: string;
  region?: string;
}) {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["anomalies", "list", mode, params],
    queryFn: async () => {
      const data = await anomalyService.list({ ...params, mode });
      // Unwrap if nested in anomalies object
      return Array.isArray(data) ? data : data?.anomalies ?? [];
    },
  });
}

export function useLatestAnomalies() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["anomalies", "latest", mode],
    queryFn: async () => {
      const data = await anomalyService.latest({ mode });
      // Unwrap if nested in anomalies object
      return Array.isArray(data) ? data : data?.anomalies ?? [];
    },
  });
}

