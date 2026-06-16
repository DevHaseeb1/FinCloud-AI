"""
Cost forecasting API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models import db_models, schemas
from app.api.dependencies import require_authenticated_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("", response_model=schemas.APIResponse)
async def get_forecast(
    days: int = Query(30, ge=1, le=365),
    service: str = Query(None),
    region: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: None = Depends(require_authenticated_user),
):
    """
    Get cost forecasts.
    
    Args:
        days: Forecast period in days
        service: Filter by service
        region: Filter by region
        skip: Pagination offset
        limit: Pagination limit
        db: Database session
        
    Returns:
        Forecast data
    """
    try:
        query = db.query(db_models.Forecast).order_by(
            db_models.Forecast.date.desc()
        )
        
        if service:
            query = query.filter(db_models.Forecast.service == service)
        if region:
            query = query.filter(db_models.Forecast.region == region)
        
        forecasts = query.offset(skip).limit(limit).all()
        
        forecast_data = [
            {
                "date": f.date.isoformat(),
                "service": f.service,
                "region": f.region,
                "predicted_cost": round(f.predicted_cost, 2),
                "lower_bound": round(f.lower_bound, 2),
                "upper_bound": round(f.upper_bound, 2),
                "confidence_interval": f"[{round(f.lower_bound, 2)}, {round(f.upper_bound, 2)}]"
            }
            for f in forecasts
        ]
        
        return schemas.APIResponse(
            status="success",
            data={"forecasts": forecast_data},
            message=f"Retrieved {len(forecast_data)} forecast records"
        )
    except Exception as e:
        logger.error(f"Error getting forecasts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/next-30-days", response_model=schemas.APIResponse)
async def get_forecast_next_30_days(
    db: Session = Depends(get_db),
    _: None = Depends(require_authenticated_user),
):
    """
    Get forecast for next 30 days.
    
    Returns:
        30-day forecast
    """
    try:
        today = datetime.now().date()
        future_date = today + timedelta(days=30)
        
        # Get forecast records for next 30 days
        forecasts = db.query(db_models.Forecast).filter(
            db_models.Forecast.date >= datetime.combine(today, datetime.min.time()),
            db_models.Forecast.date <= datetime.combine(future_date, datetime.max.time())
        ).order_by(db_models.Forecast.date).all()
        
        if not forecasts:
            return schemas.APIResponse(
                status="success",
                data={"message": "No forecast data available"},
                message="Empty forecast"
            )
        
        # Aggregate by date
        daily_forecast = {}
        for f in forecasts:
            date_key = f.date.date().isoformat()
            if date_key not in daily_forecast:
                daily_forecast[date_key] = {
                    "date": date_key,
                    "predicted_cost": 0,
                    "lower_bound": 0,
                    "upper_bound": 0
                }
            daily_forecast[date_key]["predicted_cost"] += f.predicted_cost
            daily_forecast[date_key]["lower_bound"] += f.lower_bound
            daily_forecast[date_key]["upper_bound"] += f.upper_bound
        
        forecast_list = sorted(daily_forecast.values(), key=lambda x: x["date"])
        
        # Calculate summary
        total_predicted = sum(f["predicted_cost"] for f in forecast_list)
        avg_daily = total_predicted / len(forecast_list) if forecast_list else 0
        
        summary = {
            "period": "next 30 days",
            "total_predicted_cost": round(total_predicted, 2),
            "average_daily_cost": round(avg_daily, 2),
            "forecast_records": len(forecast_list),
            "forecasts": forecast_list
        }
        
        return schemas.APIResponse(
            status="success",
            data=summary,
            message="30-day forecast retrieved"
        )
    except Exception as e:
        logger.error(f"Error getting 30-day forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-service", response_model=schemas.APIResponse)
async def get_forecast_by_service(
    service: str = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: None = Depends(require_authenticated_user),
):
    """
    Get forecast for specific service.
    
    Args:
        service: Service name
        days: Forecast period
        db: Database session
        
    Returns:
        Service forecast
    """
    try:
        future_date = datetime.now() + timedelta(days=days)
        
        forecasts = db.query(db_models.Forecast).filter(
            db_models.Forecast.service == service,
            db_models.Forecast.date <= future_date
        ).order_by(db_models.Forecast.date).all()
        
        if not forecasts:
            return schemas.APIResponse(
                status="success",
                data={"message": f"No forecast data for service {service}"},
                message="Empty forecast"
            )
        
        forecast_data = [
            {
                "date": f.date.isoformat(),
                "predicted_cost": round(f.predicted_cost, 2),
                "lower_bound": round(f.lower_bound, 2),
                "upper_bound": round(f.upper_bound, 2)
            }
            for f in forecasts
        ]
        
        total_predicted = sum(f["predicted_cost"] for f in forecast_data)
        
        return schemas.APIResponse(
            status="success",
            data={
                "service": service,
                "total_predicted_cost": round(total_predicted, 2),
                "forecasts": forecast_data
            },
            message=f"Retrieved forecast for {service}"
        )
    except Exception as e:
        logger.error(f"Error getting service forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))
