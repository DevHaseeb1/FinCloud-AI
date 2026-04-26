"use client";

import { useQuery } from "@tanstack/react-query";
import { forecastService } from "@/services/forecastService";
import { useDataMode } from "@/lib/mode";

export function useForecast() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["forecast", "base", mode],
    queryFn: () => forecastService.base({ mode }),
  });
}

export function useForecastNext30() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["forecast", "next30", mode],
    queryFn: () => forecastService.next30({ mode }),
  });
}

