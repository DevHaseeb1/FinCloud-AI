"use client";

import { useQuery } from "@tanstack/react-query";
import { forecastService } from "@/services/forecastService";
import { useDataMode } from "@/lib/mode";

export function useForecast() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["forecast", "base", mode],
    queryFn: async () => {
      const data = await forecastService.base({ mode });
      // Unwrap if nested in forecasts object
      return Array.isArray(data) ? data : data?.forecasts ?? [];
    },
  });
}

export function useForecastNext30() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["forecast", "next30", mode],
    queryFn: async () => {
      const data = await forecastService.next30({ mode });
      // Unwrap if nested in forecasts object
      const forecasts = Array.isArray(data) ? data : data?.forecasts ?? [];
      // Map API field names to component field names
      return forecasts.map((f: any) => ({
        ...f,
        predicted: f.predicted_cost,
        lower: f.lower_bound,
        upper: f.upper_bound,
        date: f.date,
      }));
    },
  });
}

