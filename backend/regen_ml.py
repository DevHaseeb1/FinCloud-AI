"""
Regenerate all ML model results from existing database data.
Works with the current DB schema (no user_id/cost_zscore columns).
Usage: python regen_ml.py
"""
import sys
import json
import logging
import traceback
from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from app.core.settings import get_settings
from app.services.anomaly_detection import AnomalyDetectionService
from app.services.forecasting import ForecastingService
from app.services.optimization import OptimizationService

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def reload_raw_for_anomaly(df_raw: pd.DataFrame) -> pd.DataFrame:
    anom = df_raw.rename(columns={'usage_quantity': 'usage_amount'}).copy()
    anom['account_id'] = anom.get('account_id', 'unknown').fillna('unknown').astype(str)
    anom['usage_type'] = anom.get('instance_type', 'unknown').fillna('unknown').astype(str)
    anom['usage_amount'] = anom.get('usage_amount', 0).fillna(0).astype(float)
    anom['environment'] = 'unknown'
    anom['line_item_type'] = 'unknown'
    anom['resource_id'] = 'unknown'
    anom['operation'] = 'unknown'
    anom['product_family'] = 'unknown'
    anom['pricing_term'] = 'unknown'
    return anom


def main():
    settings = get_settings()
    engine = create_engine(settings.database_url)

    logger.info("Loading data...")
    df_raw = pd.read_sql("SELECT * FROM raw_cost_data", engine, parse_dates=['timestamp'])
    df_proc = pd.read_sql("SELECT * FROM processed_cost_data", engine, parse_dates=['date'])
    logger.info(f"Raw: {len(df_raw)} rows, Processed: {len(df_proc)} rows")

    if df_proc.empty:
        logger.error("No processed data. Upload a CSV first.")
        return

    conn = engine.connect()

    try:
        # ── 1. ANOMALY DETECTION ──────────────────────────────────────────────
        logger.info("Running anomaly detection...")
        conn.execute(text("DELETE FROM anomalies"))

        anomaly_df = reload_raw_for_anomaly(df_raw)
        if len(anomaly_df) >= 10:
            svc = AnomalyDetectionService(contamination=0.02)
            svc.train(anomaly_df)
            results = svc.detect_anomalies(anomaly_df)

            # Use a sample since 105k rows is too much
            sample = results.sample(n=min(1000, len(results)), random_state=42) if len(results) > 1000 else results

            rows = []
            for _, row in sample.iterrows():
                expl = row.get('explanation', {})
                if isinstance(expl, dict):
                    expl = json.dumps(expl)
                rows.append({
                    'date': row.get('date', row['timestamp']),
                    'service': str(row['service'])[:100],
                    'region': str(row['region'])[:100],
                    'anomaly_score': float(row.get('anomaly_score', 0)),
                    'anomaly_flag': bool(row.get('anomaly_flag', False)),
                    'cost_value': float(row.get('cost', 0)),
                    'explanation': str(expl),
                })

            if rows:
                stmt = text(
                    "INSERT INTO anomalies (date, service, region, anomaly_score, "
                    "anomaly_flag, cost_value, explanation) VALUES "
                    "(:date, :service, :region, :score, :flag, :cost, :expl)"
                )
                for r in rows:
                    conn.execute(stmt, {
                        'date': r['date'],
                        'service': r['service'],
                        'region': r['region'],
                        'score': r['anomaly_score'],
                        'flag': r['anomaly_flag'],
                        'cost': r['cost_value'],
                        'expl': r['explanation'],
                    })
                n_anom = sum(1 for r in rows if r['anomaly_flag'])
                logger.info(f"Saved {len(rows)} anomaly records ({n_anom} flagged, "
                           f"sample of {len(sample)} from {len(results)} total)")

        # ── 2. FORECASTING ────────────────────────────────────────────────────
        logger.info("Running forecasting...")
        conn.execute(text("DELETE FROM forecasts"))

        if len(df_proc) >= 10:
            fc = ForecastingService(forecast_periods=30)
            fc.train(df_proc, service='all')
            forecast = fc.forecast_total_cost()

            stmt = text(
                "INSERT INTO forecasts (date, service, region, predicted_cost, lower_bound, upper_bound) "
                "VALUES (:date, :service, :region, :pred, :lower, :upper)"
            )
            for _, row in forecast.iterrows():
                conn.execute(stmt, {
                    'date': row['date'],
                    'service': 'all',
                    'region': 'all',
                    'pred': float(row.get('predicted_cost', 0)),
                    'lower': float(row.get('lower_bound', 0)),
                    'upper': float(row.get('upper_bound', 0)),
                })
            min_pred = forecast['predicted_cost'].min()
            logger.info(f"Saved {len(forecast)} forecast records (min_pred=${min_pred:.2f})")

        # ── 3. RECOMMENDATIONS ────────────────────────────────────────────────
        logger.info("Generating recommendations...")
        conn.execute(text("DELETE FROM recommendations"))

        if len(df_proc) >= 5:
            opt = OptimizationService()
            recs = opt.get_recommendations(df_proc, top_n=10)

            stmt = text(
                "INSERT INTO recommendations "
                "(service, region, recommendation_type, suggestion, estimated_savings, confidence_score, priority) "
                "VALUES (:service, :region, :type, :suggestion, :savings, :confidence, :priority)"
            )
            for r in recs:
                conn.execute(stmt, {
                    'service': str(r.get('service', 'all'))[:100],
                    'region': str(r.get('region', 'all'))[:100],
                    'type': str(r.get('recommendation_type', 'optimization'))[:100],
                    'suggestion': str(r.get('suggestion', '')),
                    'savings': float(r.get('estimated_savings', 0)),
                    'confidence': float(r.get('confidence_score', 0.5)),
                    'priority': int(r.get('priority', 4)),
                })
            total_savings = sum(r.get('estimated_savings', 0) for r in recs)
            logger.info(f"Saved {len(recs)} recommendations (total=${total_savings:.2f})")

        conn.commit()
        logger.info("=== REGENERATION COMPLETE ===")

    except Exception as e:
        conn.rollback()
        logger.error(f"Regeneration failed: {e}\n{traceback.format_exc()}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
