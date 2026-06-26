"""
Batch anomaly scoring job.

Loads historical billing data, runs AnomalyDetectionService.detect_anomalies(),
and persists the results — including the explanation dict and its extracted
numeric fields — to the anomalies table.

Usage:
    python -m app.services.score_anomalies --from 2026-01-01 --to 2026-06-24
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime
from typing import Optional

import pandas as pd

from app.core.database import SessionLocal
from app.models import db_models
from app.services.anomaly_detection import AnomalyDetectionService

logger = logging.getLogger(__name__)


def score_and_persist(
    df: pd.DataFrame,
    user_id: int,
    contamination: float = 0.01,
    batch_label: Optional[str] = None,
) -> int:
    """
    Score a billing DataFrame and write anomaly rows (including explanation)
    into the database.

    Args:
        df: Billing data with columns expected by AnomalyDetectionService.
        user_id: The user ID to associate anomaly records with.
        contamination: Passed to AnomalyDetectionService.
        batch_label: Optional string stored for observability.

    Returns:
        Number of anomaly rows inserted.
    """
    svc = AnomalyDetectionService(contamination=contamination)
    result = svc.detect_anomalies(df)

    anomalies = result[result["anomaly_flag"] == 1]
    if anomalies.empty:
        logger.info("No anomalies detected in batch.")
        return 0

    db = SessionLocal()
    try:
        inserted = 0
        for _, row in anomalies.iterrows():
            raw_explanation = row.get("explanation")

            if isinstance(raw_explanation, dict):
                explanation_json = json.dumps(raw_explanation)
                cost_zscore = raw_explanation.get("cost_zscore")
                cost_ratio_p95 = raw_explanation.get("cost_ratio_p95")
                daily_spend_zscore = raw_explanation.get("daily_spend_zscore")
                cost_per_unit_ratio = raw_explanation.get("cost_per_unit_ratio")
                error_count = raw_explanation.get("error_count")
            else:
                explanation_json = None
                cost_zscore = None
                cost_ratio_p95 = None
                daily_spend_zscore = None
                cost_per_unit_ratio = None
                error_count = None

            ts = row.get("timestamp")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)

            anomaly_record = db_models.Anomaly(
                user_id=user_id,
                date=ts or pd.Timestamp.now(),
                service=str(row.get("service", "unknown")),
                region=str(row.get("region", "unknown")),
                anomaly_score=float(row.get("anomaly_score", 0)),
                anomaly_flag=True,
                cost_value=float(row.get("cost", 0)),
                explanation=explanation_json,
                cost_zscore=cost_zscore,
                cost_ratio_p95=cost_ratio_p95,
                daily_spend_zscore=daily_spend_zscore,
                cost_per_unit_ratio=cost_per_unit_ratio,
                error_count=error_count,
            )
            db.add(anomaly_record)
            inserted += 1

        db.commit()
        logger.info(
            "Scored and persisted %d anomalies (batch=%s).",
            inserted,
            batch_label or "unspecified",
        )
        return inserted
    except Exception:
        db.rollback()
        logger.exception("Failed to persist batch anomalies.")
        raise
    finally:
        db.close()


def run_batch(
    start_date: date,
    end_date: date,
    user_id: int,
    source_query=None,
    contamination: float = 0.01,
) -> int:
    """
    Convenience wrapper for scheduled invocation.

    Args:
        start_date: Inclusive start.
        end_date: Inclusive end.
        user_id: The user ID to associate anomaly records with.
        source_query: Optional callable that returns a DataFrame given
                      (start_date, end_date). If None, a simple SQLAlchemy
                      query against raw_cost_data is used.
        contamination: Passed to AnomalyDetectionService.

    Returns:
        Number of anomaly rows inserted.
    """
    if source_query is None:
        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            rows = (
                db.query(db_models.RawCostData)
                .filter(
                    db_models.RawCostData.timestamp >= start_date,
                    db_models.RawCostData.timestamp <= end_date,
                )
                .all()
            )
            df = pd.DataFrame(
                [
                    {
                        "timestamp": r.timestamp,
                        "service": r.service,
                        "region": r.region,
                        "cost": r.cost,
                        "usage_amount": r.usage_quantity or 0,
                        "account_id": r.account_id or "unknown",
                        "usage_type": "unknown",
                        "environment": "unknown",
                        "instance_type": r.instance_type or "unknown",
                    }
                    for r in rows
                ]
            )
        finally:
            db.close()
    else:
        df = source_query(start_date, end_date)

    if df.empty:
        logger.info("No billing data found for %s — %s.", start_date, end_date)
        return 0

    return score_and_persist(df, user_id=user_id, contamination=contamination, batch_label=f"{start_date}_{end_date}")


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Batch anomaly scorer")
    parser.add_argument("--from", dest="start", type=date.fromisoformat, required=True)
    parser.add_argument("--to", dest="end", type=date.fromisoformat, required=True)
    parser.add_argument("--user-id", type=int, default=1, help="User ID to associate anomalies with")
    parser.add_argument("--contamination", type=float, default=0.01)
    args = parser.parse_args()

    count = run_batch(args.start, args.end, user_id=args.user_id, contamination=args.contamination)
    logger.info("Batch complete. %d anomalies persisted.", count)
