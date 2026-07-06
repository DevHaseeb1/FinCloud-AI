"""
Standalone ML evaluation script.
Loads data from DB, runs all 3 models, reports metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.ml.prophet_model import ProphetForecastingModel
from app.ml.random_forest import RandomForestOptimizer
from app.services.anomaly_detection import AnomalyDetectionService, FEATURE_COLS

logger = logging.getLogger(__name__)


def evaluate_anomaly_detection(
    service: AnomalyDetectionService,
    df: pd.DataFrame,
) -> Dict:
    results = service.detect_anomalies(df)
    n_total = len(results)
    n_anomalies = int(results['anomaly_flag'].sum())

    score_dist = results['anomaly_score'].describe().to_dict()
    severity_dist = results['severity'].value_counts().to_dict() if 'severity' in results.columns else {}

    return {
        'n_total': n_total,
        'n_anomalies': n_anomalies,
        'anomaly_rate': round(n_anomalies / max(n_total, 1), 4),
        'score_mean': round(score_dist.get('mean', 0), 4),
        'score_std': round(score_dist.get('std', 0), 4),
        'score_p95': round(score_dist.get('75%', 0), 4),
        'severity_distribution': {k: int(v) for k, v in severity_dist.items()},
        'top_features': FEATURE_COLS[:5],
    }


def evaluate_forecast(
    model: ProphetForecastingModel,
    df: pd.DataFrame,
    periods: int = 30,
) -> Dict:
    train_df = df.groupby('date').agg({'total_cost': 'sum'}).reset_index()
    train_df.columns = ['ds', 'y']

    split = int(len(train_df) * 0.8)
    if split < 14:
        return {'error': 'Insufficient data for evaluation'}

    train = train_df.iloc[:split].copy()
    train['ds'] = train['ds'].dt.tz_localize(None)
    test = train_df.iloc[split:].copy()
    test['ds'] = test['ds'].dt.tz_localize(None)

    model.train(train, model_name='eval', tune=False)
    forecast = model.forecast(periods=len(test), model_name='eval')

    forecast = forecast.merge(
        test.rename(columns={'y': 'actual'}),
        on='ds', how='left'
    )
    forecast = forecast.dropna(subset=['actual'])

    if len(forecast) == 0:
        return {'error': 'No overlapping dates for evaluation'}

    actuals = forecast['actual'].values
    # yhat is already expm1'd by the model's forecast() method
    predicted = forecast['yhat'].values
    mape = np.mean(np.abs((actuals - predicted) / (actuals + 1e-6))) * 100
    rmse = np.sqrt(np.mean((actuals - predicted) ** 2))
    mae = np.mean(np.abs(actuals - predicted))

    within_ci = ((actuals >= forecast['yhat_lower'].values) &
                 (actuals <= forecast['yhat_upper'].values)).mean()

    return {
        'mape_pct': round(mape, 2),
        'rmse': round(rmse, 2),
        'mae': round(mae, 2),
        'within_95pct_ci': round(float(within_ci), 4),
        'n_test': len(forecast),
        'n_train': len(train),
    }


def evaluate_recommendations(
    model: RandomForestOptimizer,
    df: pd.DataFrame,
) -> Dict:
    from app.services.optimization import OptimizationService
    svc = OptimizationService()
    svc.model = model

    svc.train(df)

    importances = svc.get_feature_importance()
    top_5 = dict(list(importances.items())[:5])

    recs = svc.get_recommendations(df, top_n=20)
    total_savings = sum(r['estimated_savings'] for r in recs)
    by_type = {}
    for r in recs:
        t = r['recommendation_type']
        by_type[t] = by_type.get(t, 0) + 1

    return {
        'n_recommendations': len(recs),
        'total_estimated_savings': round(total_savings, 2),
        'by_type': by_type,
        'top_features': top_5,
        'oob_score': round(model.metrics.oob_score, 4) if model.metrics and model.metrics.oob_score else None,
    }


def run_full_evaluation(
    anomaly_df: pd.DataFrame,
    processed_df: pd.DataFrame,
    user_id: int = 1,
) -> Dict:
    logger.info("=== ML Evaluation Run ===")

    anomaly_svc = AnomalyDetectionService(contamination=0.02)
    anomaly_svc.train(anomaly_df)
    anomaly_results = evaluate_anomaly_detection(anomaly_svc, anomaly_df)

    forecast_model = ProphetForecastingModel()
    forecast_results = evaluate_forecast(forecast_model, processed_df)

    opt_model = RandomForestOptimizer()
    rec_results = evaluate_recommendations(opt_model, processed_df)

    summary = {
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'anomaly_detection': anomaly_results,
        'forecasting': forecast_results,
        'recommendations': rec_results,
    }

    logger.info(f"Evaluation complete: {len(anomaly_df)} anomaly rows, "
                f"{len(processed_df)} processed rows")
    return summary


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("Run this via: python -m app.ml.evaluation")
    print("Or import run_full_evaluation() and call with your DataFrames.")
