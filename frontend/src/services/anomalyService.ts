import { getData } from "@/services/api";
import type { Anomaly } from "@/types/apiTypes";

export const anomalyService = {
  list: (opts?: { start?: string; end?: string; service?: string; region?: string; mode?: string }) =>
    getData<Anomaly[]>("/anomalies", { params: opts }),

  latest: (opts?: { mode?: string }) => getData<Anomaly[]>("/anomalies/latest", { params: opts }),
};

