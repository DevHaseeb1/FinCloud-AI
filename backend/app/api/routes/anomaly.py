"""
Anomaly detection API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models import db_models, schemas

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("", response_model=schemas.APIResponse)
async def get_anomalies(
    days: int = Query(30, ge=1, le=365),
    min_score: float = Query(0.5, ge=0, le=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get detected anomalies.
    
    Args:
        days: Number of days to retrieve
        min_score: Minimum anomaly score
        skip: Pagination offset
        limit: Pagination limit
        db: Database session
        
    Returns:
        List of anomalies
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        anomalies = db.query(db_models.Anomaly).filter(
            db_models.Anomaly.date >= start_date,
            db_models.Anomaly.anomaly_flag == 1,
            db_models.Anomaly.anomaly_score >= min_score
        ).order_by(
            db_models.Anomaly.anomaly_score.desc()
        ).offset(skip).limit(limit).all()
        
        total_count = db.query(db_models.Anomaly).filter(
            db_models.Anomaly.date >= start_date,
            db_models.Anomaly.anomaly_flag == 1,
            db_models.Anomaly.anomaly_score >= min_score
        ).count()
        
        anomaly_data = [
            {
                "id": a.id,
                "date": a.date.isoformat(),
                "service": a.service,
                "region": a.region,
                "cost_value": round(a.cost_value, 2),
                "anomaly_score": round(a.anomaly_score, 4),
                "explanation": a.explanation
            }
            for a in anomalies
        ]
        
        return schemas.APIResponse(
            status="success",
            data={
                "anomalies": anomaly_data,
                "total_count": total_count,
                "returned_count": len(anomaly_data)
            },
            message=f"Retrieved {len(anomaly_data)} anomalies"
        )
    except Exception as e:
        logger.error(f"Error getting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest", response_model=schemas.APIResponse)
async def get_latest_anomalies(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get latest detected anomalies.
    
    Args:
        limit: Number of anomalies to retrieve
        db: Database session
        
    Returns:
        Latest anomalies
    """
    try:
        anomalies = db.query(db_models.Anomaly).filter(
            db_models.Anomaly.anomaly_flag == 1
        ).order_by(
            db_models.Anomaly.date.desc()
        ).limit(limit).all()
        
        anomaly_data = [
            {
                "id": a.id,
                "date": a.date.isoformat(),
                "service": a.service,
                "region": a.region,
                "cost_value": round(a.cost_value, 2),
                "anomaly_score": round(a.anomaly_score, 4),
                "explanation": a.explanation
            }
            for a in anomalies
        ]
        
        return schemas.APIResponse(
            status="success",
            data={"anomalies": anomaly_data},
            message=f"Retrieved {len(anomaly_data)} latest anomalies"
        )
    except Exception as e:
        logger.error(f"Error getting latest anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-service", response_model=schemas.APIResponse)
async def get_anomalies_by_service(
    service: str = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get anomalies for a specific service.
    
    Args:
        service: Service name
        days: Number of days
        db: Database session
        
    Returns:
        Anomalies for service
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        anomalies = db.query(db_models.Anomaly).filter(
            db_models.Anomaly.service == service,
            db_models.Anomaly.date >= start_date,
            db_models.Anomaly.anomaly_flag == 1
        ).order_by(
            db_models.Anomaly.date.desc()
        ).all()
        
        anomaly_data = [
            {
                "id": a.id,
                "date": a.date.isoformat(),
                "service": a.service,
                "region": a.region,
                "cost_value": round(a.cost_value, 2),
                "anomaly_score": round(a.anomaly_score, 4),
                "explanation": a.explanation
            }
            for a in anomalies
        ]
        
        return schemas.APIResponse(
            status="success",
            data={"anomalies": anomaly_data},
            message=f"Retrieved {len(anomaly_data)} anomalies for {service}"
        )
    except Exception as e:
        logger.error(f"Error getting anomalies by service: {e}")
        raise HTTPException(status_code=500, detail=str(e))
