"""
AWS Lambda handler for Kinesis stream of billing rows.

Each record is a JSON blob with the same schema as the training DataFrame.
The handler loads a pre-trained AnomalyDetectionService from S3 (or a local
artifacts directory), calls predict_single(), and persists the result —
including the explanation dict — to the anomalies table.

Environment variables:
    ARTIFACTS_DIR: Path to saved model artifacts (default: /opt/ml/anomaly/)
"""

from __future__ import annotations

import json
import logging
import os
from base64 import b64decode
from datetime import datetime

from app.core.database import SessionLocal
from app.models import db_models
from app.services.anomaly_detection import AnomalyDetectionService

logger = logging.getLogger(__name__)

_ARTIFACTS_DIR = os.environ.get("ARTIFACTS_DIR", "/opt/ml/anomaly/")
_DEFAULT_USER_ID = int(os.environ.get("DEFAULT_USER_ID", "1"))
_svc: AnomalyDetectionService | None = None


def _get_service() -> AnomalyDetectionService:
    global _svc
    if _svc is None:
        _svc = AnomalyDetectionService.load_artifacts(_ARTIFACTS_DIR)
    return _svc


def _persist_anomaly(row_dict: dict, prediction: dict, user_id: int) -> None:
    """Write a single anomaly row (with explanation) to the anomalies table."""
    explanation = prediction.get("explanation") or {}

    db = SessionLocal()
    try:
        ts = row_dict.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))

        record = db_models.Anomaly(
            user_id=user_id,
            date=ts or datetime.utcnow(),
            service=str(row_dict.get("service", "unknown")),
            region=str(row_dict.get("region", "unknown")),
            anomaly_score=float(prediction.get("anomaly_score", 0)),
            anomaly_flag=prediction.get("is_anomaly", False),
            cost_value=float(row_dict.get("cost", 0)),
            explanation=json.dumps(explanation) if explanation else None,
            cost_zscore=explanation.get("cost_zscore"),
            cost_ratio_p95=explanation.get("cost_ratio_p95"),
            daily_spend_zscore=explanation.get("daily_spend_zscore"),
            cost_per_unit_ratio=explanation.get("cost_per_unit_ratio"),
            error_count=explanation.get("error_count"),
        )
        db.add(record)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to persist Kinesis anomaly row.")
        raise
    finally:
        db.close()


def lambda_handler(event: dict, context=None) -> dict:
    """
    AWS Lambda entry point for Kinesis stream processing.

    Expected event shape (Kinesis -> Lambda):
    {
        "Records": [
            {
                "kinesis": {
                    "data": "<base64-encoded JSON>"
                }
            }
        ]
    }

    Each decoded record is a dict with the billing row fields.
    """
    svc = _get_service()
    processed = 0
    anomalies_found = 0
    daily_acct_cache: dict[str, float] = {}

    for record in event.get("Records", []):
        try:
            payload = b64decode(record["kinesis"]["data"]).decode("utf-8")
            row = json.loads(payload)
        except Exception:
            logger.warning("Skipping malformed Kinesis record.")
            continue

        processed += 1

        acct = str(row.get("account_id", "unknown"))
        if acct not in daily_acct_cache:
            daily_acct_cache[acct] = 0.0
        daily_total = daily_acct_cache[acct]

        # Real-time inference
        prediction = svc.predict_single(row, daily_acct_total=daily_total)

        if prediction.get("is_anomaly"):
            _persist_anomaly(row, prediction, user_id=_DEFAULT_USER_ID)
            anomalies_found += 1

        # Update cache with this row's cost for next call
        daily_acct_cache[acct] = daily_total + float(row.get("cost", 0))

    logger.info(
        "Kinesis batch: %d records processed, %d anomalies persisted.",
        processed,
        anomalies_found,
    )

    return {
        "batchItemFailures": [],
        "processed": processed,
        "anomalies_persisted": anomalies_found,
    }
