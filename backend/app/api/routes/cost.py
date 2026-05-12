"""
Cost-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import logging

from app.core.database import get_db
from app.models import db_models, schemas
from app.utils.helpers import (
    aggregate_by_service, 
    aggregate_by_region, 
    calculate_percentage,
    format_currency,
    get_trend,
    get_table_date_range
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cost", tags=["cost"])


@router.get("/summary", response_model=schemas.APIResponse)
async def get_cost_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get cost summary for specified period.
    
    Args:
        days: Number of days to summarize
        db: Database session
        
    Returns:
        Cost summary response
    """
    try:
        data_min, data_max = get_table_date_range(db, db_models.ProcessedCostData, "date")
        if data_max is None:
            return schemas.APIResponse(
                status="success",
                data={"message": "No cost data found in database"},
                message="Empty database"
            )
        
        start_date = data_max - timedelta(days=days)
        
        # Query processed costs
        costs = db.query(db_models.ProcessedCostData).filter(
            db_models.ProcessedCostData.date >= start_date
        ).all()
        
        if not costs:
            return schemas.APIResponse(
                status="success",
                data={"message": "No cost data found for specified period"},
                message="Empty period"
            )
        
        # Calculate summary metrics
        total_cost = sum(c.total_cost for c in costs)
        avg_daily_cost = total_cost / days
        
        # Group by service
        services_costs = {}
        for cost in costs:
            if cost.service not in services_costs:
                services_costs[cost.service] = 0
            services_costs[cost.service] += cost.total_cost
        
        highest_service = max(services_costs, key=services_costs.get)
        lowest_service = min(services_costs, key=services_costs.get)
        
        summary = {
            "total_cost": round(total_cost, 2),
            "average_daily_cost": round(avg_daily_cost, 2),
            "highest_service": highest_service,
            "highest_service_cost": round(services_costs[highest_service], 2),
            "lowest_service": lowest_service,
            "lowest_service_cost": round(services_costs[lowest_service], 2),
            "period_start": start_date.isoformat(),
            "period_end": data_max.isoformat(),
            "num_records": len(costs)
        }
        
        return schemas.APIResponse(
            status="success",
            data=summary,
            message="Cost summary retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting cost summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeseries", response_model=schemas.APIResponse)
async def get_cost_timeseries(
    days: int = Query(30, ge=1, le=365),
    service: str = Query(None),
    region: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get cost time series data.
    
    Args:
        days: Number of days
        service: Filter by service
        region: Filter by region
        db: Database session
        
    Returns:
        Time series data
    """
    try:
        data_min, data_max = get_table_date_range(db, db_models.ProcessedCostData, "date")
        if data_max is None:
            return schemas.APIResponse(
                status="success",
                data={"timeseries": []},
                message="No cost data found in database"
            )
        
        start_date = data_max - timedelta(days=days)
        
        query = db.query(db_models.ProcessedCostData).filter(
            db_models.ProcessedCostData.date >= start_date
        )
        
        if service:
            query = query.filter(db_models.ProcessedCostData.service == service)
        if region:
            query = query.filter(db_models.ProcessedCostData.region == region)
        
        costs = query.order_by(db_models.ProcessedCostData.date).all()
        
        timeseries = [
            {
                "timestamp": c.date.isoformat(),
                "value": round(c.total_cost, 2),
                "service": c.service,
                "region": c.region
            }
            for c in costs
        ]
        
        return schemas.APIResponse(
            status="success",
            data={"timeseries": timeseries},
            message=f"Retrieved {len(timeseries)} time series points"
        )
    except Exception as e:
        logger.error(f"Error getting cost timeseries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-breakdown", response_model=schemas.APIResponse)
async def get_service_breakdown(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get cost breakdown by service.
    
    Args:
        days: Number of days
        db: Database session
        
    Returns:
        Service breakdown
    """
    try:
        data_min, data_max = get_table_date_range(db, db_models.ProcessedCostData, "date")
        if data_max is None:
            return schemas.APIResponse(
                status="success",
                data={"breakdown": []},
                message="No cost data found in database"
            )
        
        start_date = data_max - timedelta(days=days)
        
        costs = db.query(db_models.ProcessedCostData).filter(
            db_models.ProcessedCostData.date >= start_date
        ).all()
        
        # Aggregate by service
        service_costs = {}
        for cost in costs:
            if cost.service not in service_costs:
                service_costs[cost.service] = 0
            service_costs[cost.service] += cost.total_cost
        
        total = sum(service_costs.values())
        
        breakdown = []
        for service, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True):
            breakdown.append({
                "service": service,
                "total_cost": round(cost, 2),
                "percentage": round(calculate_percentage(cost, total), 2),
                "trend": "up"  # Could be calculated from previous period
            })
        
        return schemas.APIResponse(
            status="success",
            data={"breakdown": breakdown},
            message="Service breakdown retrieved"
        )
    except Exception as e:
        logger.error(f"Error getting service breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/region-breakdown", response_model=schemas.APIResponse)
async def get_region_breakdown(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get cost breakdown by region.
    
    Args:
        days: Number of days
        db: Database session
        
    Returns:
        Region breakdown
    """
    try:
        data_min, data_max = get_table_date_range(db, db_models.ProcessedCostData, "date")
        if data_max is None:
            return schemas.APIResponse(
                status="success",
                data={"breakdown": []},
                message="No cost data found in database"
            )
        
        start_date = data_max - timedelta(days=days)
        
        costs = db.query(db_models.ProcessedCostData).filter(
            db_models.ProcessedCostData.date >= start_date
        ).all()
        
        # Aggregate by region
        region_costs = {}
        region_services = {}
        for cost in costs:
            if cost.region not in region_costs:
                region_costs[cost.region] = 0
                region_services[cost.region] = set()
            region_costs[cost.region] += cost.total_cost
            region_services[cost.region].add(cost.service)
        
        total = sum(region_costs.values())
        
        breakdown = []
        for region, cost in sorted(region_costs.items(), key=lambda x: x[1], reverse=True):
            breakdown.append({
                "region": region,
                "total_cost": round(cost, 2),
                "percentage": round(calculate_percentage(cost, total), 2),
                "services_count": len(region_services[region])
            })
        
        return schemas.APIResponse(
            status="success",
            data={"breakdown": breakdown},
            message="Region breakdown retrieved"
        )
    except Exception as e:
        logger.error(f"Error getting region breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))
