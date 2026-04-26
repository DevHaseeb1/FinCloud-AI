export type ApiEnvelope<T> = {
  status: "success" | "error";
  data: T;
  message?: string;
};

export type CostSummary = {
  total_cost?: number;
  monthly_cost?: number;
  cost_change_pct?: number;
  currency?: string;
};

export type CostTimeseriesPoint = {
  date: string;
  cost: number;
};

export type BreakdownItem = {
  name: string;
  cost: number;
  pct?: number;
};

export type Anomaly = {
  id?: string | number;
  timestamp?: string;
  service?: string;
  region?: string;
  cost?: number;
  expected_cost?: number;
  anomaly_score?: number;
  severity?: "low" | "medium" | "high";
  description?: string;
};

export type ForecastPoint = {
  date: string;
  actual?: number;
  predicted: number;
  lower?: number;
  upper?: number;
};

export type Recommendation = {
  id?: string | number;
  title?: string;
  description?: string;
  estimated_savings?: number;
  priority?: "low" | "medium" | "high";
  category?: string;
};

export type UploadResult = {
  rows_ingested?: number;
  dataset_id?: string;
};

