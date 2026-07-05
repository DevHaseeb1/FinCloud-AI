"""
Anomaly Detection Service — FinCloud-AI
========================================
Upgraded implementation using Isolation Forest with account-normalized
feature engineering from the AWS Cost Anomaly Detection notebook.

Key improvements over v1:
  - Account + service + usage_type normalized features (cost_zscore,
    cost_ratio_p95, cost_ratio_mean) so multi-tenant accounts are judged
    against their own baselines, not a global average
  - Frequency encoding for categorical columns instead of label encoding
    (no more "Other" bucket getting 100% anomaly rate)
  - RobustScaler (median/IQR) instead of StandardScaler (mean/std) —
    outliers no longer distort the scaler
  - Credit/refund rows excluded from training (negative costs are not anomalies)
  - Daily account-level spend z-score to catch account-wide spending spikes
  - Cost efficiency feature: cost_per_unit_ratio detects cost spikes with
    no corresponding usage increase
  - Structured explanation dict with real diagnostic values (not score buckets)
  - Artifact persistence: baseline stats + encoding maps saved to disk so
    inference on new rows works without retraining
  - Cold-start handling for unseen account/service combinations

Usage
------
  from app.ml.anomaly_detection_service import AnomalyDetectionService

  svc = AnomalyDetectionService(contamination=0.01)
  svc.train(df_historical)
  svc.save_artifacts("models/anomaly/")

  # On new incoming rows:
  svc2 = AnomalyDetectionService.load_artifacts("models/anomaly/")
  result_df = svc2.detect_anomalies(df_new_rows)
  top10 = svc2.get_top_anomalies(result_df, top_n=10)

Expected DataFrame columns
---------------------------
Required:
  account_id, service, usage_type, cost, usage_amount, timestamp

Baseline group key (defines one normalisation unit):
  account_id + service + usage_type + region + environment + instance_type
  + operation + product_family
  Each unique combination gets its own cost baseline, so a prod EC2 spike
  in us-east-1 never contaminates the baseline for dev EC2 in ap-southeast-1.

Optional but strongly recommended (available in your dataset):
  region, environment, instance_type, operation, product_family  ← used in group key
  line_item_type, resource_id, pricing_term  ← used as frequency-encoded features
  normalized_usage, cpu_utilization, memory_utilization,
  network_in_mb, network_out_mb, latency_ms, throughput,
  invocations, duration_ms, error_count,
  availability_percent, status_check_failed
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

# The grouping key that defines "one baseline unit".
#
# Why these five columns?
#   account_id    — multi-tenant isolation: each customer judged against themselves
#   service       — EC2 and S3 have completely different cost distributions
#   usage_type    — EBS:VolumeUsage.gp3 vs BoxUsage:t3.micro behave differently
#   region        — us-east-1 pricing differs from ap-southeast-1; a spike in one
#                   should not inflate the baseline for the other
#   environment   — prod spend patterns are fundamentally different from dev/staging;
#                   mixing them would suppress dev anomalies and create prod false alarms
#   instance_type — a t3.micro and a p4d.24xlarge must never share a cost baseline
#
# Cold-start note: the more granular the key, the fewer rows per bucket.
# New account+region+env+instance combinations fall back to neutral values
# until enough history accumulates (see predict_single cold-start handling).
_GRP_KEY = ["account_id", "service", "usage_type", "region", "environment", "instance_type", "operation", "product_family"]

# All features fed to Isolation Forest — order matters for inference.
# If you add a feature, append it here AND add its computation in
# _build_normalized_features(). Never change the order of existing entries
# without regenerating all saved artifacts.
FEATURE_COLS = [
    "cost_zscore",
    "cost_ratio_p95",
    "cost_ratio_mean",
    "daily_spend_zscore",
    "cost_per_unit_ratio",
    "log_cost",
    "log_usage_amount",
    "cost_momentum_3d",
    "service_spend_share",
    "spike_persistence",
    "cost_autocorr_lag1",
    "region_cost_spread",
    "mad_zscore",
    "iqr_outlier",
    "cusum",
    "hour",
    "dayofweek",
    "is_weekend",
    "month",
    "service_freq",
    "usage_type_freq",
    "region_freq",
    "environment_freq",
    "instance_type_freq",
    "operation_freq",
    "product_family_freq",
    "pricing_term_freq",
    "resource_id_freq",
    "line_item_type_freq",
]

# Artifact filenames# Artifact filenames written/read by save_artifacts() / load_artifacts()
_ARTIFACT_FILES = {
    "model":        "isolation_forest_model.pkl",
    "scaler":       "feature_scaler.pkl",
    "feature_cols": "feature_columns.json",
    "score_norm":   "score_norm_params.json",
    "baseline":     "account_service_baseline.csv",
    "enc_maps":     "encoding_maps.json",
}


# ── Main service class ─────────────────────────────────────────────────────────

class AnomalyDetectionService:
    """
    Cost anomaly detection using Isolation Forest with account-normalized
    feature engineering.

    Lifecycle
    ---------
    1. Instantiate with desired contamination.
    2. Call train(df) on historical billing data.
    3. Call save_artifacts(dir) to persist the model + lookup tables.
    4. On new data: call detect_anomalies(df) or load a saved instance
       with AnomalyDetectionService.load_artifacts(dir).
    """

    def __init__(self, contamination: float = 0.01) -> None:
        """
        Args:
            contamination: Expected fraction of anomalies in the data.
                           0.01 = 1% (good default for AWS billing).
                           Increase to 0.02–0.05 if you are missing obvious
                           anomalies; decrease to 0.005 if too many false alarms.
        """
        self.contamination = contamination

        # Sklearn objects — populated by train() or load_artifacts()
        self._model:  Optional[IsolationForest] = None
        self._scaler: Optional[RobustScaler]    = None

        # Lookup tables built during training — needed for inference
        self._baseline:     Optional[pd.DataFrame] = None   # per account+svc+type stats
        self._baseline_idx: Optional[dict]         = None   # fast dict lookup
        self._svc_freq:     Optional[dict]         = None   # service         → frequency
        self._ut_freq:      Optional[dict]         = None   # usage_type      → frequency
        self._region_freq:  Optional[dict]         = None   # region          → frequency
        self._env_freq:     Optional[dict]         = None   # environment     → frequency
        self._itype_freq:   Optional[dict]         = None   # instance_type   → frequency
        self._op_freq:      Optional[dict]         = None   # operation       → frequency
        self._pf_freq:      Optional[dict]         = None   # product_family  → frequency
        self._pt_freq:      Optional[dict]         = None   # pricing_term    → frequency
        self._rid_freq:     Optional[dict]         = None   # resource_id     → frequency
        self._lit_freq:     Optional[dict]         = None   # line_item_type  → frequency

        # Score normalization params (min/max of decision_function on train set)
        self._score_min: float = 0.0
        self._score_max: float = 1.0

        # Beta calibration params — maps raw scores to calibrated p-values
        self._beta_a: float = 1.0
        self._beta_b: float = 1.0

        self.is_trained: bool = False

    # ══════════════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════════════════════════════════

    def train(self, df: pd.DataFrame) -> None:
        """
        Train the anomaly detection model on historical billing data.

        Steps performed:
          1. Parse and validate timestamps
          2. Exclude credits/refunds (negative costs)
          3. Build account-normalized features
          4. Fit RobustScaler + Isolation Forest
          5. Compute score normalization params

        Args:
            df: Historical billing DataFrame. Must contain at minimum:
                account_id, service, usage_type, cost, usage_amount, timestamp.
        """
        logger.info("AnomalyDetectionService: starting training")

        df_clean = self._prepare_dataframe(df)

        # Step 1 — Exclude credits/refunds from training.
        # Negative costs are accounting entries, not cost anomalies.
        # Also use line_item_type when available for more accurate filtering.
        credit_mask = df_clean["cost"] < 0
        if "line_item_type" in df_clean.columns:
            credit_mask |= df_clean["line_item_type"].str.lower().isin(["credit", "refund"])
        n_credits = credit_mask.sum()
        df_train = df_clean[~credit_mask].copy()
        logger.info(
            f"Excluded {n_credits:,} credit/refund rows. "
            f"Training on {len(df_train):,} rows."
        )

        if len(df_train) < 10:
            raise ValueError(
                "Insufficient training data — need at least 10 non-credit rows."
            )

        # Step 2 — Build all features (modifies df_train in-place, returns it)
        df_feat = self._build_all_features(df_train)

        # Step 3 — Assemble the feature matrix
        X = self._to_feature_matrix(df_feat)
        logger.info(f"Feature matrix shape: {X.shape}")

        # Step 4 — Fit RobustScaler.
        # RobustScaler uses median + IQR so extreme outliers (the very thing
        # we are trying to detect) do not distort the scaling parameters.
        self._scaler = RobustScaler()
        X_scaled = self._scaler.fit_transform(X)

        # Step 5 — Fit Isolation Forest
        self._model = IsolationForest(
            n_estimators=300,    # More trees → more stable decision boundaries
            max_samples=512,     # Subsample size per tree
            max_features=0.75,   # 75% of features per tree — adds diversity
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1,
        )
        self._model.fit(X_scaled)

        # Step 6 — Compute score normalization parameters on the training set
        # so we can map raw decision_function output → [0, 1] for inference.
        raw_scores = self._model.decision_function(X_scaled)
        self._score_min = float(raw_scores.min())
        self._score_max = float(raw_scores.max())

        # Step 7 — Fit Beta distribution to normalized scores for calibrated
        # p-values. p < 0.01 → "High", p < 0.05 → "Medium", else "Low".
        train_scores = 1.0 - (raw_scores - self._score_min) / (self._score_max - self._score_min + 1e-9)
        train_scores = np.clip(train_scores, 1e-6, 1 - 1e-6)
        try:
            self._beta_a, self._beta_b, *_ = stats.beta.fit(train_scores, floc=0, fscale=1)
        except Exception:
            self._beta_a, self._beta_b = 1.0, 1.0

        n_anomalies = (self._model.predict(X_scaled) == -1).sum()
        logger.info(
            f"Training complete. "
            f"Anomalies in training set: {n_anomalies:,} / {len(df_train):,} "
            f"({100 * n_anomalies / len(df_train):.2f}%)"
        )

        self.is_trained = True

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score a batch of billing rows for anomalies.

        If the model has not been trained yet, it trains on the input data
        first (useful for one-shot exploratory use; not recommended for
        production — call train() on historical data separately).

        Args:
            df: Billing DataFrame with the same schema as the training data.

        Returns:
            A copy of df with four additional columns:
              - anomaly_flag  (int)  : 1 = anomaly, 0 = normal
              - anomaly_score (float): 0–1 where 1 is most anomalous
              - is_credit     (int)  : 1 if this row was a credit/refund
              - explanation   (dict) : diagnostic values driving the score
        """
        if not self.is_trained:
            logger.warning(
                "Model not trained — training on input data. "
                "For production, call train() on historical data first."
            )
            self.train(df)

        df_clean = self._prepare_dataframe(df)

        # Tag credits but still score them (they will get low anomaly scores
        # naturally, but we surface the flag so the UI can filter them)
        df_clean["is_credit"] = (df_clean["cost"] < 0).astype(int)

        df_feat = self._build_all_features(df_clean)
        X = self._to_feature_matrix(df_feat)
        X_scaled = self._scaler.transform(X)

        labels     = self._model.predict(X_scaled)          # -1 = anomaly, 1 = normal
        raw_scores = self._model.decision_function(X_scaled)

        # Normalize raw scores to [0, 1] using training-set min/max.
        # Score of 1.0 = most anomalous.
        anomaly_scores = 1.0 - (
            (raw_scores - self._score_min)
            / (self._score_max - self._score_min + 1e-9)
        )
        anomaly_scores = np.clip(anomaly_scores, 0.0, 1.0)
        anomaly_flags  = (labels == -1).astype(int)

        # Calibrate via Beta p-value: p < 0.01 → "High", p < 0.05 → "Medium"
        safe_scores  = np.clip(anomaly_scores, 1e-6, 1 - 1e-6)
        p_values     = stats.beta.cdf(safe_scores, self._beta_a, self._beta_b)
        calibrated   = np.where(p_values < 0.01, "High",
                        np.where(p_values < 0.05, "Medium", "Low"))
        # Override flag: only call it an anomaly if calibrated is High or Medium
        calibrated_flags = ((calibrated == "High") | (calibrated == "Medium")).astype(int)

        result = df_feat.copy()
        result["anomaly_flag"]  = calibrated_flags
        result["anomaly_score"] = anomaly_scores
        result["severity"]      = calibrated

        # Build structured explanation for each row
        result["explanation"] = [
            self._build_explanation(row, flag, score)
            for (_, row), flag, score
            in zip(result.iterrows(), anomaly_flags, anomaly_scores)
        ]

        n_anomalies = int(anomaly_flags.sum())
        logger.info(
            f"detect_anomalies: {n_anomalies} anomalies "
            f"in {len(result)} rows ({100 * n_anomalies / len(result):.2f}%)"
        )

        return result

    def get_top_anomalies(
        self,
        df: pd.DataFrame,
        top_n: int = 10,
    ) -> pd.DataFrame:
        """
        Return the top-N most anomalous rows sorted by anomaly_score descending.

        Args:
            df:    DataFrame already processed by detect_anomalies().
            top_n: Number of rows to return.

        Returns:
            Subset of df, sorted by anomaly_score descending.
        """
        if "anomaly_flag" not in df.columns:
            raise ValueError(
                "DataFrame has not been processed by detect_anomalies(). "
                "Call detect_anomalies(df) first."
            )
        return (
            df[df["anomaly_flag"] == 1]
            .nlargest(top_n, "anomaly_score")
            .reset_index(drop=True)
        )

    # ══════════════════════════════════════════════════════════════════════════
    # PERSISTENCE
    # ══════════════════════════════════════════════════════════════════════════

    def save_artifacts(self, directory: str) -> None:
        """
        Persist all model artifacts to disk.

        Saved files:
          isolation_forest_model.pkl  — the trained Isolation Forest
          feature_scaler.pkl          — the fitted RobustScaler
          feature_columns.json        — ordered feature list (inference needs this)
          score_norm_params.json      — min/max for score normalization
          account_service_baseline.csv— per account+service+type+region+env+instance stats
          encoding_maps.json          — service/usage_type/region/environment/instance_type frequency dicts

        Args:
            directory: Directory path. Created if it does not exist.
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save artifacts — model has not been trained yet.")

        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

        joblib.dump(self._model,  path / _ARTIFACT_FILES["model"])
        joblib.dump(self._scaler, path / _ARTIFACT_FILES["scaler"])

        with open(path / _ARTIFACT_FILES["feature_cols"], "w") as f:
            json.dump(FEATURE_COLS, f, indent=2)

        with open(path / _ARTIFACT_FILES["score_norm"], "w") as f:
            json.dump(
                {
                    "score_min": self._score_min,
                    "score_max": self._score_max,
                    "beta_a":    self._beta_a,
                    "beta_b":    self._beta_b,
                },
                f,
                indent=2,
            )

        self._baseline.to_csv(path / _ARTIFACT_FILES["baseline"], index=False)

        with open(path / _ARTIFACT_FILES["enc_maps"], "w") as f:
            json.dump(
                {
                    "service_freq":       self._svc_freq,
                    "usage_type_freq":    self._ut_freq,
                    "region_freq":        self._region_freq,
                    "environment_freq":   self._env_freq,
                    "instance_type_freq": self._itype_freq,
                    "operation_freq":     self._op_freq,
                    "product_family_freq":self._pf_freq,
                    "pricing_term_freq":  self._pt_freq,
                    "resource_id_freq":   self._rid_freq,
                    "line_item_type_freq":self._lit_freq,
                },
                f,
                indent=2,
            )

        logger.info(f"Artifacts saved to: {path.resolve()}")

    @classmethod
    def load_artifacts(cls, directory: str) -> "AnomalyDetectionService":
        """
        Load a previously trained service from disk.

        Args:
            directory: Directory where save_artifacts() wrote its files.

        Returns:
            A fully initialised AnomalyDetectionService ready for inference.
        """
        path = Path(directory)

        for key, fname in _ARTIFACT_FILES.items():
            if not (path / fname).exists():
                raise FileNotFoundError(
                    f"Missing artifact '{fname}' in '{path}'. "
                    "Re-train the model and call save_artifacts()."
                )

        instance = cls.__new__(cls)

        instance._model  = joblib.load(path / _ARTIFACT_FILES["model"])
        instance._scaler = joblib.load(path / _ARTIFACT_FILES["scaler"])

        with open(path / _ARTIFACT_FILES["score_norm"]) as f:
            norm = json.load(f)
        instance._score_min = norm["score_min"]
        instance._score_max = norm["score_max"]
        instance._beta_a    = norm.get("beta_a", 1.0)
        instance._beta_b    = norm.get("beta_b", 1.0)

        instance._baseline = pd.read_csv(path / _ARTIFACT_FILES["baseline"])
        for col in ("account_id", "region", "environment", "instance_type", "operation", "product_family"):
            if col in instance._baseline.columns:
                instance._baseline[col] = instance._baseline[col].astype(str)
            else:
                instance._baseline[col] = "unknown"
        instance._baseline_idx = {
            (r.account_id, r.service, r.usage_type,
             r.region, r.environment, r.instance_type,
             r.operation, r.product_family): r
            for _, r in instance._baseline.iterrows()
        }

        with open(path / _ARTIFACT_FILES["enc_maps"]) as f:
            enc = json.load(f)
        instance._svc_freq    = enc["service_freq"]
        instance._ut_freq     = enc["usage_type_freq"]
        instance._region_freq = enc["region_freq"]
        instance._env_freq    = enc["environment_freq"]
        instance._itype_freq  = enc["instance_type_freq"]
        instance._op_freq     = enc.get("operation_freq", {})
        instance._pf_freq     = enc.get("product_family_freq", {})
        instance._pt_freq     = enc.get("pricing_term_freq", {})
        instance._rid_freq    = enc.get("resource_id_freq", {})
        instance._lit_freq    = enc.get("line_item_type_freq", {})

        instance.contamination = instance._model.contamination
        instance.is_trained    = True

        logger.info(f"Artifacts loaded from: {path.resolve()}")
        return instance

    # ══════════════════════════════════════════════════════════════════════════
    # SINGLE-ROW INFERENCE  (for real-time / streaming use)
    # ══════════════════════════════════════════════════════════════════════════

    def predict_single(self, row: dict, daily_acct_total: float = 0.0) -> dict:
        """
        Score a single billing row in real time.

        Intended for streaming pipelines where rows arrive one at a time from
        an AWS Cost & Usage Report or CUR export.

        NOTE: daily_acct_total must be pre-computed outside this method by
        summing today's cost for this account_id from your DB or a Redis cache.
        Without it, daily_spend_zscore will default to 0 (neutral).

        Args:
            row:               Dict with the same keys as the training DataFrame.
            daily_acct_total:  Today's total spend for this account (pre-computed).

        Returns:
            {
              "is_anomaly":    bool,
              "anomaly_score": float (0–1),
              "explanation":   dict with diagnostic values
            }
        """
        if not self.is_trained:
            raise RuntimeError("Model has not been trained. Call train() first.")

        key = (
            str(row.get("account_id", "")),
            row.get("service", ""),
            row.get("usage_type", ""),
            row.get("region", "unknown"),
            row.get("environment", "unknown"),
            row.get("instance_type", "unknown"),
            row.get("operation", "unknown"),
            row.get("product_family", "unknown"),
        )
        b = self._baseline_idx.get(key) if self._baseline_idx else None

        # ── Baseline stats for this account+service combination ───────────────
        # Fall back to safe neutral values if this is a new combination
        # (cold start). Scores will be unreliable until enough history exists.
        mean_cost = float(b.mean_cost)   if b is not None else 0.0
        std_cost  = float(b.std_cost)    if b is not None else 0.001
        p95_cost  = float(b.p95_cost)    if b is not None else 0.01
        median_cost = float(b.median_cost) if b is not None else 0.0
        daily_mean = float(b.daily_mean) if (b is not None and hasattr(b, "daily_mean")) else 0.0
        daily_std  = float(b.daily_std)  if (b is not None and hasattr(b, "daily_std"))  else 0.001

        cost         = float(row.get("cost", 0.0))
        usage_amount = float(row.get("usage_amount", 0.0)) or 1.0

        ts = pd.to_datetime(row.get("timestamp", pd.Timestamp.now()), utc=True, errors="coerce")

        cost_per_unit       = cost / usage_amount
        cost_per_unit_ratio = float(np.clip(cost_per_unit / (mean_cpu + 1e-9), 0, 100))

        mad_cost  = float(b.mad_cost)  if b is not None else 0.001
        q1_cost   = float(b.q1_cost)   if b is not None else 0.0
        q3_cost   = float(b.q3_cost)   if b is not None else 0.001

        feat = {
            "cost_zscore":         float(np.clip((cost - mean_cost) / (std_cost + 1e-9), -10, 10)),
            "cost_ratio_p95":      float(np.clip(cost / (p95_cost  + 1e-9), 0, 100)),
            "cost_ratio_mean":     float(np.clip(cost / (mean_cost + 1e-9), 0, 100)),
            "daily_spend_zscore":  float(np.clip((daily_acct_total - daily_mean) / (daily_std + 1e-9), -10, 10)),
            "cost_per_unit_ratio": cost_per_unit_ratio,
            "log_cost":            float(np.log1p(max(cost, 0))),
            "log_usage_amount":    float(np.log1p(max(usage_amount, 0))),
            "cost_momentum_3d":    1.0,
            "service_spend_share": float(np.clip(cost / (daily_acct_total + 1e-9), 0, 1)),
            "spike_persistence":   0,
            "cost_autocorr_lag1":  0.0,
            "region_cost_spread":  0.0,
            "mad_zscore":          float(np.clip(0.6745 * (cost - median_cost) / (mad_cost + 1e-9), -10, 10)),
            "iqr_outlier":         float(np.clip((cost - q3_cost) / (q3_cost - q1_cost + 1e-9), 0, 20) if cost > q3_cost else 0.0),
            "cusum":               0.0,
            "hour":       ts.hour      if ts is not pd.NaT else 0,
            "dayofweek":  ts.dayofweek if ts is not pd.NaT else 0,
            "is_weekend": int(ts.dayofweek >= 5) if ts is not pd.NaT else 0,
            "month":      ts.month     if ts is not pd.NaT else 1,
            "service_freq":       self._svc_freq.get(row.get("service",        ""), 0),
            "usage_type_freq":    self._ut_freq.get( row.get("usage_type",     ""), 0),
            "region_freq":        self._region_freq.get(row.get("region",        "unknown"), 0),
            "environment_freq":   self._env_freq.get(   row.get("environment",   "unknown"), 0),
            "instance_type_freq": self._itype_freq.get( row.get("instance_type", "unknown"), 0),
            "operation_freq":       self._op_freq.get( row.get("operation",       "unknown"), 0),
            "product_family_freq":  self._pf_freq.get( row.get("product_family",  "unknown"), 0),
            "pricing_term_freq":    self._pt_freq.get( row.get("pricing_term",    "unknown"), 0),
            "resource_id_freq":     self._rid_freq.get(row.get("resource_id",     "unknown"), 0),
            "line_item_type_freq":  self._lit_freq.get(row.get("line_item_type",  "unknown"), 0),
        }

        X = np.array([[feat[c] for c in FEATURE_COLS]], dtype=np.float64)
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        X_scaled = self._scaler.transform(X)

        label = self._model.predict(X_scaled)[0]
        raw   = float(self._model.decision_function(X_scaled)[0])
        score = float(np.clip(
            1.0 - (raw - self._score_min) / (self._score_max - self._score_min + 1e-9),
            0.0, 1.0,
        ))

        is_anomaly = label == -1

        return {
            "is_anomaly":    is_anomaly,
            "anomaly_score": round(score, 4),
            "explanation": {
                "cost_zscore":         round(feat["cost_zscore"], 2),
                "cost_ratio_p95":      round(feat["cost_ratio_p95"], 2),
                "cost_ratio_mean":     round(feat["cost_ratio_mean"], 2),
                "daily_spend_zscore":  round(feat["daily_spend_zscore"], 2),
                "cost_per_unit_ratio": round(feat["cost_per_unit_ratio"], 2),
                "mad_zscore":          round(feat["mad_zscore"], 2),
                "human_readable":      self._human_readable_explanation(feat, is_anomaly, score),
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # PRIVATE — DATA PREPARATION
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse timestamps, cast types, fill optional group-key columns,
        and sort chronologically. Does NOT filter — returns a copy.

        Group-key columns that may be absent in some datasets are filled
        with the string 'unknown' so the groupby never raises a KeyError
        and cold-start handling in the baseline lookup takes over naturally.
        """
        df = df.copy()
        if "account_id" not in df.columns:
            df["account_id"] = "unknown"
        df["account_id"] = df["account_id"].astype(str)
        df["timestamp"]  = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

        # Fill optional group-key columns — present in the FinCloud dataset
        # but guard against missing columns in unit tests / synthetic data.
        for col in ("region", "environment", "instance_type", "usage_type", "operation", "product_family"):
            if col not in df.columns:
                df[col] = "unknown"
            else:
                df[col] = df[col].fillna("unknown").astype(str)

        # Fill optional frequency-encoded columns (not in group key)
        for col in ("line_item_type", "resource_id", "pricing_term"):
            if col not in df.columns:
                df[col] = "unknown"
            else:
                df[col] = df[col].fillna("unknown").astype(str)

        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

    def _build_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Full feature engineering pipeline. Runs in sequence:
          1. Temporal features
          2. Frequency encoding for categorical columns
          3. Account-normalized cost features
          4. Daily account spend z-score
          5. Cost-per-unit efficiency ratio
          6. Log transforms
          7. Build + store the baseline lookup (training only)

        Returns the same DataFrame with all feature columns added.
        """
        df = df.copy()

        # ── 1. Temporal ───────────────────────────────────────────────────────
        df["hour"]       = df["timestamp"].dt.hour
        df["dayofweek"]  = df["timestamp"].dt.dayofweek
        df["day"]        = df["timestamp"].dt.day
        df["month"]      = df["timestamp"].dt.month
        df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)
        df["date"]       = df["timestamp"].dt.date

        # ── 2. Frequency encoding ─────────────────────────────────────────────
        # Each categorical column is encoded as its fraction of total rows.
        # Common values → high score, rare values → low score.
        #
        # Why not label encoding?
        #   Label encoding assigns arbitrary integers (EC2=0, S3=1, ...) which
        #   implies a spurious ordering. Worse, any unseen category at inference
        #   time would be assigned the catch-all "Other" bucket, which the model
        #   then learns to flag as anomalous simply because it's rare — not
        #   because it's actually unusual cost behaviour.
        #
        # Why frequency encoding catches real anomalies:
        #   A row in a rarely-used region (e.g. ap-east-1) or on an unusual
        #   instance type (p4d.24xlarge in a dev account) naturally gets a low
        #   frequency score, which the forest treats as a mild signal. Combined
        #   with a high cost_zscore it pushes the row toward anomalous. A common
        #   region + unusual cost is the more important signal.
        #
        # Frequency maps are built once during training and reused at inference.
        # Unseen categories at inference time map to 0 (rarest possible) via
        # .fillna(0) — which is conservative and appropriate.
        if self._svc_freq is None:
            self._svc_freq    = df["service"].value_counts(normalize=True).to_dict()
            self._ut_freq     = df["usage_type"].value_counts(normalize=True).to_dict()
            self._region_freq = df["region"].value_counts(normalize=True).to_dict()
            self._env_freq    = df["environment"].value_counts(normalize=True).to_dict()
            self._itype_freq  = df["instance_type"].value_counts(normalize=True).to_dict()
            self._op_freq     = df["operation"].value_counts(normalize=True).to_dict()
            self._pf_freq     = df["product_family"].value_counts(normalize=True).to_dict()
            self._pt_freq     = df["pricing_term"].value_counts(normalize=True).to_dict()
            self._rid_freq    = df["resource_id"].value_counts(normalize=True).to_dict()
            self._lit_freq    = df["line_item_type"].value_counts(normalize=True).to_dict()

        df["service_freq"]       = df["service"].map(self._svc_freq).fillna(0)
        df["usage_type_freq"]    = df["usage_type"].map(self._ut_freq).fillna(0)
        df["region_freq"]        = df["region"].map(self._region_freq).fillna(0)
        df["environment_freq"]   = df["environment"].map(self._env_freq).fillna(0)
        df["instance_type_freq"] = df["instance_type"].map(self._itype_freq).fillna(0)
        df["operation_freq"]       = df["operation"].map(self._op_freq).fillna(0)
        df["product_family_freq"]  = df["product_family"].map(self._pf_freq).fillna(0)
        df["pricing_term_freq"]    = df["pricing_term"].map(self._pt_freq).fillna(0)
        df["resource_id_freq"]     = df["resource_id"].map(self._rid_freq).fillna(0)
        df["line_item_type_freq"]  = df["line_item_type"].map(self._lit_freq).fillna(0)

        # ── 3. Account-normalized cost features ───────────────────────────────
        # All cost signals are computed relative to the baseline for
        # THIS account + THIS service + THIS usage_type.
        # A $100 spike for an account that normally spends $10 is treated
        # the same as a $1000 spike for one that normally spends $1000.
        grp = df.groupby(_GRP_KEY)["cost"]

        df["acct_svc_mean"]   = grp.transform("mean")
        df["acct_svc_std"]    = grp.transform("std").fillna(0)
        df["acct_svc_p95"]    = grp.transform(lambda x: x.quantile(0.95))
        df["acct_svc_median"] = grp.transform("median")

        # cost_zscore: how many SDs from this account+service's typical cost?
        # Clipped to [-10, 10] to prevent extreme values destabilising the forest.
        df["cost_zscore"] = (
            (df["cost"] - df["acct_svc_mean"])
            / (df["acct_svc_std"] + 1e-9)
        ).clip(-10, 10)

        # cost_ratio_p95: > 1.0 means this row exceeded the 95th percentile
        # for this specific account + service combination
        df["cost_ratio_p95"] = (
            df["cost"] / (df["acct_svc_p95"] + 1e-9)
        ).clip(0, 100)

        # cost_ratio_mean: how many multiples of the usual cost for this bucket?
        df["cost_ratio_mean"] = (
            df["cost"] / (df["acct_svc_mean"] + 1e-9)
        ).clip(0, 100)

        # ── 4. Daily account spend z-score ────────────────────────────────────
        # Detects account-wide spending spikes that no single row would reveal.
        # E.g. 10 services each spending 2× their normal: individually ok,
        # but together the daily total would spike.
        daily_acct = (
            df.groupby(["account_id", "date"])["cost"]
            .sum()
            .reset_index()
            .rename(columns={"cost": "daily_acct_total"})
        )
        df = df.merge(daily_acct, on=["account_id", "date"], how="left")

        acct_daily_mean = df.groupby("account_id")["daily_acct_total"].transform("mean")
        acct_daily_std  = df.groupby("account_id")["daily_acct_total"].transform("std").fillna(0)

        df["daily_spend_zscore"] = (
            (df["daily_acct_total"] - acct_daily_mean)
            / (acct_daily_std + 1e-9)
        ).clip(-10, 10)

        # ── 5. Cost-per-unit efficiency ratio ─────────────────────────────────
        # A spike in cost WITH no usage increase is a very strong anomaly signal.
        # E.g. an EC2 instance charged at 10× its normal rate with the same CPU hours.
        usage_safe = df["usage_amount"].replace(0, np.nan)
        df["cost_per_unit"] = (df["cost"] / usage_safe).fillna(0)

        # Clip at 99.9th pct * 10 to avoid astronomically large values
        cpu_cap = df["cost"].quantile(0.999) * 10
        df["cost_per_unit"] = df["cost_per_unit"].clip(0, cpu_cap)

        cpu_mean = df.groupby(_GRP_KEY)["cost_per_unit"].transform("mean")
        df["cost_per_unit_ratio"] = (
            df["cost_per_unit"] / (cpu_mean + 1e-9)
        ).clip(0, 100)

        # ── 6. Log transforms ─────────────────────────────────────────────────
        df["log_cost"]         = np.log1p(df["cost"].clip(lower=0))
        df["log_usage_amount"] = np.log1p(df["usage_amount"].clip(lower=0))

        # ── 7. Billing-pattern features (always computable from CUR data) ────
        # cost_momentum_3d: 3-day rolling avg / 7-day rolling avg per group.
        # Values near 1 = stable; > 1 = accelerating; < 1 = decelerating.
        df = df.sort_values(["date"]).reset_index(drop=True)
        grp_date = df.groupby(_GRP_KEY)["cost"]
        df["cost_ma_3d"] = grp_date.transform(lambda x: x.rolling(3, min_periods=1).mean())
        df["cost_ma_7d"] = grp_date.transform(lambda x: x.rolling(7, min_periods=1).mean())
        df["cost_momentum_3d"] = (df["cost_ma_3d"] / (df["cost_ma_7d"] + 1e-9)).clip(0, 10)

        # service_spend_share: what % of total daily spend does this service represent?
        daily_total = df.groupby("date")["cost"].transform("sum")
        df["service_spend_share"] = (df["cost"] / (daily_total + 1e-9)).clip(0, 1)

        # spike_persistence: for each group, count consecutive days where cost
        # exceeds 1.5× the group median, going backward from this row's date.
        df["above_median"] = (df["cost"] > 1.5 * df["acct_svc_median"] + 1e-9).astype(int)
        df["spike_persistence"] = (
            grp_date.transform(
                lambda x: x.groupby((x == 0).cumsum()).cumcount() + 1
            ) * df["above_median"]
        )

        # cost_autocorr_lag1: per-group lag-1 autocorrelation of cost.
        # Low magnitude → pattern break (stochastic); high → consistent.
        def _autocorr_lag1(series):
            s = series.values
            if len(s) < 3 or np.std(s[:-1]) < 1e-9 or np.std(s[1:]) < 1e-9:
                return 0.0
            return float(np.corrcoef(s[:-1], s[1:])[0, 1])
        df["cost_autocorr_lag1"] = df.groupby(_GRP_KEY)["cost"].transform(_autocorr_lag1)

        # region_cost_spread: (max - min) / mean across regions for this date
        region_stats = df.groupby("date")["cost"].agg(["max", "min", "mean"]).reset_index()
        region_stats["region_cost_spread"] = (
            (region_stats["max"] - region_stats["min"]) / (region_stats["mean"] + 1e-9)
        ).clip(0, 20)
        df = df.merge(region_stats[["date", "region_cost_spread"]], on="date", how="left")

        # ── 8. Statistical scores (robust anomaly signals) ──────────────────────
        # mad_zscore: modified z-score using MAD (more robust than mean/std).
        grp_mad = df.groupby(_GRP_KEY)["cost"]
        median_cost = grp_mad.transform("median")
        mad = grp_mad.transform(lambda x: np.median(np.abs(x - x.median())))
        df["mad_zscore"] = (
            0.6745 * (df["cost"] - median_cost) / (mad + 1e-9)
        ).clip(-10, 10)

        # iqr_outlier: how far beyond Q3 (positive) or Q1 (negative) in IQR units.
        q1 = grp_mad.transform(lambda x: x.quantile(0.25))
        q3 = grp_mad.transform(lambda x: x.quantile(0.75))
        iqr = q3 - q1
        df["iqr_outlier"] = np.where(
            iqr > 1e-9,
            ((df["cost"] - q3) / iqr).clip(0, 20),
            0.0
        )

        # cusum: cumulative sum of deviations from group mean (chronological).
        df["cost_deviation"] = df["cost"] - df["acct_svc_mean"]
        df["cusum"] = (
            df.groupby(_GRP_KEY)["cost_deviation"]
            .transform(lambda x: x.cumsum())
        )
        # Scale cusum to prevent unbounded growth
        cusum_std = df["cusum"].std()
        if cusum_std > 1e-9:
            df["cusum"] = (df["cusum"] / cusum_std).clip(-10, 10)
        else:
            df["cusum"] = 0.0

        # ── 9. Build / update baseline lookup table ───────────────────────────
        new_baseline = (
            df.groupby(_GRP_KEY)
            .agg(
                mean_cost   = ("cost",         "mean"),
                std_cost    = ("cost",         "std"),
                p95_cost    = ("cost",         lambda x: x.quantile(0.95)),
                median_cost = ("cost",         "median"),
                q1_cost     = ("cost",         lambda x: x.quantile(0.25)),
                q3_cost     = ("cost",         lambda x: x.quantile(0.75)),
                mad_cost    = ("cost",         lambda x: np.median(np.abs(x - x.median()))),
                mean_cpu    = ("cost_per_unit","mean"),
                daily_mean  = ("daily_acct_total", "mean"),
                daily_std   = ("daily_acct_total", "std"),
            )
            .fillna(0)
            .reset_index()
        )
        self._baseline = new_baseline
        self._baseline_idx = {
            (r.account_id, r.service, r.usage_type,
             r.region, r.environment, r.instance_type,
             r.operation, r.product_family): r
            for _, r in new_baseline.iterrows()
        }

        return df

    def _to_feature_matrix(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extract the ordered feature matrix from a fully-engineered DataFrame.
        Replaces any NaN / Inf with 0 before returning.
        """
        X = df[FEATURE_COLS].fillna(0).replace([np.inf, -np.inf], 0).values
        return X.astype(np.float64)

    # ══════════════════════════════════════════════════════════════════════════
    # PRIVATE — EXPLANATION GENERATION
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _build_explanation(row: pd.Series, flag: int, score: float) -> dict:
        """
        Build a structured explanation dict for one row.
        Returns diagnostic feature values + a human-readable summary string.
        """
        feat_vals = {
            "cost_zscore":         round(float(row.get("cost_zscore", 0)),         2),
            "cost_ratio_p95":      round(float(row.get("cost_ratio_p95", 0)),      2),
            "cost_ratio_mean":     round(float(row.get("cost_ratio_mean", 0)),     2),
            "daily_spend_zscore":  round(float(row.get("daily_spend_zscore", 0)),  2),
            "cost_per_unit_ratio": round(float(row.get("cost_per_unit_ratio", 0)), 2),
        }
        is_anomaly = flag == 1
        feat_vals["human_readable"] = AnomalyDetectionService._human_readable_explanation(
            feat_vals, is_anomaly, score
        )
        return feat_vals

    @staticmethod
    def _human_readable_explanation(feat: dict, is_anomaly: bool, score: float) -> str:
        if not is_anomaly:
            return "Normal cost pattern"

        reasons = []

        zscore = feat.get("cost_zscore", 0)
        if abs(zscore) >= 3:
            direction = "above" if zscore > 0 else "below"
            reasons.append(
                f"Cost is {abs(zscore):.1f}× SDs {direction} this account's baseline"
            )

        p95 = feat.get("cost_ratio_p95", 0)
        if p95 > 5:
            reasons.append(
                f"Cost is {p95:.1f}× the 95th-pct for this account+service"
            )
        elif p95 > 2:
            reasons.append(
                f"Cost exceeds the 95th-pct for this account+service ({p95:.1f}×)"
            )

        daily_z = feat.get("daily_spend_zscore", 0)
        if abs(daily_z) >= 3:
            reasons.append(
                f"Account daily total is {abs(daily_z):.1f} SDs above normal"
            )

        cpu_ratio = feat.get("cost_per_unit_ratio", 0)
        if cpu_ratio > 5:
            reasons.append(
                f"Cost-per-unit is {cpu_ratio:.1f}× the account baseline "
                f"(cost spike without usage increase)"
            )

        mad_z = feat.get("mad_zscore", 0)
        if abs(mad_z) >= 3.5:
            reasons.append(
                f"Robust z-score is {abs(mad_z):.1f} — highly deviant from median"
            )

        if not reasons:
            severity = "Severe" if score > 0.875 else "Moderate" if score > 0.95 else "Minor"
            reasons.append(f"{severity} multi-factor anomaly (score: {score:.2f})")

        return "; ".join(reasons)