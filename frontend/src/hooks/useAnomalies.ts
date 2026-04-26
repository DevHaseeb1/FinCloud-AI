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
    queryFn: () => anomalyService.list({ ...params, mode }),
  });
}

export function useLatestAnomalies() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["anomalies", "latest", mode],
    queryFn: () => anomalyService.latest({ mode }),
  });
}

