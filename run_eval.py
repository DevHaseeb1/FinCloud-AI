"""
Standalone evaluation: load CSV data, run all 3 models, report accuracy.
Usage:
  python run_eval.py                    # Text output
  python run_eval.py --report           # Generate HTML report with charts
  python run_eval.py --report --output my_report.html
"""
import argparse
import logging
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ['DATABASE_URL'] = 'sqlite:///dummy.db'

logging.basicConfig(level=logging.INFO, format='%(message)s')

from app.services.anomaly_detection import AnomalyDetectionService
from app.ml.prophet_model import ProphetForecastingModel
from app.ml.random_forest import RandomForestOptimizer
from app.ml.evaluation import (
    evaluate_anomaly_detection,
    evaluate_forecast,
    evaluate_recommendations,
)
from app.services.preprocessing import DataPreprocessor

CSV_PATH = r"C:\Users\Haseeb\Desktop\FinCloud-AI\Fincloud-cur-enhanced-v2.csv"


def main():
    parser = argparse.ArgumentParser(description="FinCloud-AI Model Evaluation")
    parser.add_argument("--report", action="store_true",
                        help="Generate interactive HTML report with charts")
    parser.add_argument("--output", default="eval_report.html",
                        help="Output path for the HTML report (default: eval_report.html)")
    args = parser.parse_args()

    if args.report:
        from app.ml.eval_report import run_and_build_report
        path = run_and_build_report(CSV_PATH, output_path=args.output)
        print(f"\n{'=' * 60}")
        print(f"Interactive report saved to: {os.path.abspath(path)}")
        print(f"Open in your browser to view charts and graphs.")
        print(f"{'=' * 60}")
        return

    # ── 1. Load CSV ──────────────────────────────────────────────────────
    df_raw = pd.read_csv(CSV_PATH, low_memory=False)
    print(f"\nLoaded {len(df_raw)} rows from CSV")

    # ── 2. Preprocess ────────────────────────────────────────────────────
    # Map columns to standard format
    df_map = df_raw.rename(columns={
        'lineItem/UnblendedCost': 'cost',
        'lineItem/UsageStartDate': 'timestamp',
        'lineItem/ProductCode': 'service',
        'product/region': 'region',
        'lineItem/UsageAmount': 'usage_amount',
        'lineItem/UsageType': 'usage_type',
        'lineItem/LineItemType': 'line_item_type',
        'lineItem/ResourceId': 'resource_id',
        'lineItem/Operation': 'operation',
        'product/productFamily': 'product_family',
        'pricing/term': 'pricing_term',
        'product/instanceType': 'instance_type',
    })
    if 'timestamp' in df_map.columns:
        df_map['timestamp'] = pd.to_datetime(df_map['timestamp'], errors='coerce')
    df_map['cost'] = pd.to_numeric(df_map['cost'], errors='coerce').fillna(0)
    df_map['usage_amount'] = pd.to_numeric(df_map['usage_amount'], errors='coerce').fillna(0)
    df_map['usage_quantity'] = df_map['usage_amount']
    df_map['service'] = df_map['service'].fillna('unknown').astype(str).str.lower()
    df_map['region'] = df_map['region'].fillna('unknown').astype(str).str.lower()
    df_map['usage_type'] = df_map['usage_type'].fillna('unknown').astype(str)
    df_map['line_item_type'] = df_map['line_item_type'].fillna('Usage').astype(str)
    df_map['resource_id'] = df_map['resource_id'].fillna('unknown').astype(str)
    df_map['operation'] = df_map['operation'].fillna('unknown').astype(str)
    df_map['product_family'] = df_map['product_family'].fillna('unknown').astype(str)
    df_map['pricing_term'] = df_map['pricing_term'].fillna('unknown').astype(str)
    df_map['instance_type'] = df_map['instance_type'].fillna('unknown').astype(str)
    df_map['account_id'] = 'unknown'
    df_map['environment'] = 'unknown'

    df_map = df_map.dropna(subset=['timestamp'])

    print(f"After preprocessing: {len(df_map)} rows")

    # ── 3. Anomaly Detection ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("MODEL 1: ANOMALY DETECTION (Isolation Forest)")
    print("=" * 60)
    anomaly_svc = AnomalyDetectionService(contamination=0.02)
    anomaly_svc.train(df_map)

    # Sample if too large
    eval_df = df_map
    if len(df_map) > 5000:
        eval_df = df_map.sample(n=5000, random_state=42)
        print(f"(Sampled to {len(eval_df)} rows for anomaly detection)")

    anom_results = evaluate_anomaly_detection(anomaly_svc, eval_df)
    for k, v in anom_results.items():
        print(f"  {k}: {v}")

    # ── 4. Forecasting ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("MODEL 2: FORECASTING (Prophet)")
    print("=" * 60)
    df_proc = DataPreprocessor.full_preprocessing_pipeline(df_map)
    print(f"Processed data: {len(df_proc)} rows, date range: {df_proc['date'].min()} to {df_proc['date'].max()}")

    forecast_model = ProphetForecastingModel()
    forecast_results = evaluate_forecast(forecast_model, df_proc, periods=30)
    for k, v in forecast_results.items():
        print(f"  {k}: {v}")

    # ── 5. Recommendations ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("MODEL 3: COST OPTIMIZATION (Random Forest + XGBoost)")
    print("=" * 60)
    opt_model = RandomForestOptimizer(
        n_estimators=500,
        max_depth=15,
        anomaly_contamination=0.05,
    )
    rec_results = evaluate_recommendations(opt_model, df_proc)
    for k, v in rec_results.items():
        print(f"  {k}: {v}")

    # ── 6. Summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SUMMARY: MODEL ACCURACY METRICS")
    print("=" * 60)

    anom_rate = anom_results.get('anomaly_rate', 'N/A')
    mape = forecast_results.get('mape_pct', 'N/A')
    oob = rec_results.get('oob_score', 'N/A')

    print(f"  1. Anomaly Detection (Isolation Forest)")
    print(f"     Anomaly rate:          {anom_rate}")
    print(f"     Score mean:            {anom_results.get('score_mean', 'N/A')}")
    print(f"     Score P95:             {anom_results.get('score_p95', 'N/A')}")
    print(f"     Samples evaluated:     {anom_results.get('n_total', 'N/A')}")
    print()
    print(f"  2. Forecasting (Prophet)")
    print(f"     MAPE:                  {mape}%")
    print(f"     RMSE:                  ${forecast_results.get('rmse', 'N/A')}")
    print(f"     MAE:                   ${forecast_results.get('mae', 'N/A')}")
    print(f"     Within 95% CI:         {forecast_results.get('within_95pct_ci', 'N/A')}")
    print(f"     Training samples:      {forecast_results.get('n_train', 'N/A')}")
    print(f"     Test samples:          {forecast_results.get('n_test', 'N/A')}")
    print()
    print(f"  3. Cost Optimization (Random Forest + XGBoost)")
    print(f"     OOB R² score:          {oob}")
    print(f"     Recommendations:       {rec_results.get('n_recommendations', 'N/A')}")
    print(f"     Total savings:         ${rec_results.get('total_estimated_savings', 'N/A')}")
    print(f"     Top features:          {rec_results.get('top_features', 'N/A')}")


if __name__ == '__main__':
    main()
