export type ApiEnvelope<T> = {
  status: "success" | "error";
  data: T;
  message?: string;
};

export type CostSummary = {
  total_cost?: number;
  monthly_cost?: number;
  average_daily_cost?: number;
  cost_change_pct?: number;
  currency?: string;
  highest_service?: string;
  highest_service_cost?: number;
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

export type AnomalyExplanation = {
  cost_zscore: number;
  cost_ratio_p95: number;
  cost_ratio_mean: number;
  daily_spend_zscore: number;
  cost_per_unit_ratio: number;
  error_count: number;
  human_readable: string;
};

export type Anomaly = {
  id?: string | number;
  timestamp?: string;
  date?: string;
  service?: string;
  region?: string;
  cost?: number;
  cost_value?: number;
  expected_cost?: number;
  anomaly_score?: number;
  severity?: "low" | "medium" | "high";
  description?: string;
  explanation?: AnomalyExplanation | null;
  cost_zscore?: number | null;
  cost_ratio_p95?: number | null;
  daily_spend_zscore?: number | null;
  cost_per_unit_ratio?: number | null;
  error_count?: number | null;
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

export type RecommendationsResponse = {
  recommendations?: Recommendation[];
  total_potential_savings?: number;
};

export type UploadResult = {
  rows_ingested?: number;
  dataset_id?: string;
};

// Auth Types
export type User = {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  role: string;
  created_at: string;
  updated_at?: string;
};

export type AuthToken = {
  access_token: string;
  token_type: string;
};

export type AuthResponse = {
  user: User;
  token: AuthToken;
};

// AWS Connection types
export type AwsConnection = {
  id: number;
  name: string;
  account_id?: string;
  role_arn?: string;
  region: string;
  s3_cur_bucket?: string;
  s3_cur_prefix?: string;
  is_active: boolean;
  last_fetch_at?: string;
  last_fetch_status?: string;
  created_at: string;
  updated_at: string;
};

export type AwsSetupResponse = {
  external_id: string;
  role_name: string;
  cloudformation_url: string;
  template_download_url?: string;
};

export type AwsTestCheck = {
  check: string;
  status: "success" | "error" | "warning" | "skipped";
  message?: string;
};

export type AwsTestResponse = {
  connection_id: number;
  overall_status: "success" | "partial" | "error";
  checks: AwsTestCheck[];
};

export type AwsFetchHistory = {
  id: number;
  connection_id: number;
  source: string;
  start_date?: string;
  end_date?: string;
  rows_fetched: number;
  rows_processed: number;
  duration_seconds?: number;
  status: string;
  error_message?: string;
  created_at: string;
};

