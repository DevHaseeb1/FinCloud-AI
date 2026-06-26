import { getData } from "@/services/api";
import type { Anomaly, AnomalyExplanation } from "@/types/apiTypes";

export type AnomalyFilterParams = {
  start?: string;
  end?: string;
  service?: string;
  region?: string;
  mode?: string;
  cost_zscore_gt?: number;
  cost_ratio_p95_gt?: number;
  cost_per_unit_ratio_gt?: number;
  has_errors?: boolean;
};

export type AnomalyListResponse = {
  anomalies: Anomaly[];
  total_count?: number;
  returned_count?: number;
};

export const anomalyService = {
  list: (opts?: AnomalyFilterParams) =>
    getData<AnomalyListResponse>("/anomalies", { params: opts }),

  latest: (opts?: { mode?: string }) =>
    getData<AnomalyListResponse>("/anomalies/latest", { params: opts }),

  getById: (id: number | string) =>
    getData<Anomaly & { anomaly_flag: boolean; created_at: string }>(
      `/anomalies/${id}`,
    ),
};
