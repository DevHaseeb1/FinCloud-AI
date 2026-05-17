import { getData } from "@/services/api";
import type { ForecastPoint } from "@/types/apiTypes";

export const forecastService = {
  base: (opts?: { mode?: string }) =>
    getData<ForecastPoint[] | { forecasts: ForecastPoint[] }>("/forecast", { params: opts }),
  next30: (opts?: { mode?: string }) =>
    getData<ForecastPoint[] | { forecasts: ForecastPoint[] }>("/forecast/next-30-days", { params: opts }),
};

