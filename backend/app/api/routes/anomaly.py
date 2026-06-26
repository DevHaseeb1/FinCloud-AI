"""
Anomaly detection API endpoints.
"""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from typing import Optional

from app.core.database import get_db
from app.models import db_models, schemas
from app.utils.helpers import get_table_date_range
from app.api.dependencies import require_authenticated_user
from app.models.db_models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/anomalies", tags=["anomalies"])


def _parse_explanation(raw: Optional[str]) -> Optional[dict]:
    """Parse explanation from TEXT column into a dict (or None)."""
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def _anomaly_to_dict(a: db_models.Anomaly) -> dict:
    """Serialize an Anomaly DB row, including optional explanation fields."""
    d = {
        "id": a.id,
        "date": a.date.isoformat() if a.date else None,
        "service": a.service,
        "region": a.region,
        "cost_value": round(a.cost_value, 2) if a.cost_value else 0,
        "anomaly_score": round(a.anomaly_score, 4),
        "cost_zscore": a.cost_zscore,
        "cost_ratio_p95": a.cost_ratio_p95,
        "daily_spend_zscore": a.daily_spend_zscore,
        "cost_per_unit_ratio": a.cost_per_unit_ratio,
        "error_count": a.error_count,
        "explanation": _parse_explanation(a.explanation),
    }
    return d


@router.get("", response_model=schemas.APIResponse)
async def get_anomalies(
    days: int = Query(30, ge=1, le=365),
    min_score: float = Query(0.5, ge=0, le=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    cost_zscore_gt: Optional[float] = Query(None, ge=0),
    cost_ratio_p95_gt: Optional[float] = Query(None, ge=0),
    cost_per_unit_ratio_gt: Optional[float] = Query(None, ge=0),
    has_errors: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """
    Get detected anomalies with optional signal-based filtering.

    The `cost_zscore_gt`, `cost_ratio_p95_gt`, and `cost_per_unit_ratio_gt`
    params filter to rows where the corresponding signal exceeds the given
    threshold. `has_errors=true` filters to rows with error_count > 0.
    Multiple filter params are AND-combined.
    """
    try:
        data_min, data_max = get_table_date_range(db, db_models.Anomaly, "date", user_id=current_user.id)
        if data_max is None:
            return schemas.APIResponse(
                status="success",
                data={
                    "anomalies": [],
                    "total_count": 0,
                    "returned_count": 0,
                },
                message="No anomaly data found in database",
            )

        start_date = data_max - timedelta(days=days)

        query = db.query(db_models.Anomaly).filter(
            db_models.Anomaly.date >= start_date,
            db_models.Anomaly.user_id == current_user.id,
            db_models.Anomaly.anomaly_flag == True,
            db_models.Anomaly.anomaly_score >= min_score,
        )

        if cost_zscore_gt is not None:
            query = query.filter(db_models.Anomaly.cost_zscore > cost_zscore_gt)
        if cost_ratio_p95_gt is not None:
            query = query.filter(db_models.Anomaly.cost_ratio_p95 > cost_ratio_p95_gt)
        if cost_per_unit_ratio_gt is not None:
            query = query.filter(
                db_models.Anomaly.cost_per_unit_ratio > cost_per_unit_ratio_gt
            )
        if has_errors is True:
            query = query.filter(
                db_models.Anomaly.error_count.isnot(None)
                & (db_models.Anomaly.error_count > 0)
            )

        total_count = query.count()

        anomalies = (
            query.order_by(db_models.Anomaly.anomaly_score.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        anomaly_data = [_anomaly_to_dict(a) for a in anomalies]

        return schemas.APIResponse(
            status="success",
            data={
                "anomalies": anomaly_data,
                "total_count": total_count,
                "returned_count": len(anomaly_data),
            },
            message=f"Retrieved {len(anomaly_data)} anomalies",
        )
    except Exception as e:
        logger.error(f"Error getting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest", response_model=schemas.APIResponse)
async def get_latest_anomalies(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Get latest detected anomalies."""
    try:
        anomalies = (
            db.query(db_models.Anomaly)
            .filter(
                db_models.Anomaly.anomaly_flag == True,
                db_models.Anomaly.user_id == current_user.id,
            )
            .order_by(db_models.Anomaly.date.desc())
            .limit(limit)
            .all()
        )

        anomaly_data = [_anomaly_to_dict(a) for a in anomalies]

        return schemas.APIResponse(
            status="success",
            data={"anomalies": anomaly_data},
            message=f"Retrieved {len(anomaly_data)} latest anomalies",
        )
    except Exception as e:
        logger.error(f"Error getting latest anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-service", response_model=schemas.APIResponse)
async def get_anomalies_by_service(
    service: str = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Get anomalies for a specific service."""
    try:
        data_min, data_max = get_table_date_range(db, db_models.Anomaly, "date", user_id=current_user.id)
        if data_max is None:
            return schemas.APIResponse(
                status="success",
                data={"anomalies": []},
                message="No anomaly data found in database",
            )

        start_date = data_max - timedelta(days=days)

        anomalies = (
            db.query(db_models.Anomaly)
            .filter(
                db_models.Anomaly.service == service,
                db_models.Anomaly.date >= start_date,
                db_models.Anomaly.user_id == current_user.id,
                db_models.Anomaly.anomaly_flag == True,
            )
            .order_by(db_models.Anomaly.date.desc())
            .all()
        )

        anomaly_data = [_anomaly_to_dict(a) for a in anomalies]

        return schemas.APIResponse(
            status="success",
            data={"anomalies": anomaly_data},
            message=f"Retrieved {len(anomaly_data)} anomalies for {service}",
        )
    except Exception as e:
        logger.error(f"Error getting anomalies by service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{anomaly_id}", response_model=schemas.APIResponse)
async def get_anomaly_by_id(
    anomaly_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Get a single anomaly by ID."""
    anomaly = (
        db.query(db_models.Anomaly)
        .filter(
            db_models.Anomaly.id == anomaly_id,
            db_models.Anomaly.user_id == current_user.id,
        )
        .first()
    )
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    data = _anomaly_to_dict(anomaly)
    data["anomaly_flag"] = anomaly.anomaly_flag
    data["created_at"] = anomaly.created_at.isoformat() if anomaly.created_at else None

    return schemas.APIResponse(
        status="success",
        data=data,
        message="Anomaly retrieved successfully",
    )
