"""
Cost-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models import db_models, schemas
from app.api.dependencies import require_authenticated_user
from app.models.db_models import User
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


def _resolve_date_range(
    db: Session,
    user_id: int,
    days: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> tuple[Optional[datetime], Optional[datetime]]:
    """Compute (start, end) date bounds.

    Priority:
    1. Explicit start / end params (from frontend date picker)
    2. Rolling window from data_max: data_max - days
    3. Full range (data_min, data_max)
    """
    data_min, data_max = get_table_date_range(db, db_models.ProcessedCostData, "date", user_id=user_id)
    if data_max is None:
        return None, None

    actual_start = data_min
    actual_end = data_max

    if end is not None:
        actual_end = min(end, data_max)
    if start is not None:
        actual_start = start
    elif days is not None:
        actual_start = max(data_max - timedelta(days=days), data_min)

    return actual_start, actual_end


@router.get("", response_model=schemas.APIResponse)
async def get_cost_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Get cost overview over the full available date range."""
    data_min, data_max = get_table_date_range(db, db_models.ProcessedCostData, "date", user_id=current_user.id)
    if data_max is None:
        return schemas.APIResponse(
            status="success",
            data={"total_cost": 0, "monthly_cost": 0, "cost_change_pct": 0},
            message="No cost data found",
        )
    all_costs = db.query(db_models.ProcessedCostData).filter(
        db_models.ProcessedCostData.date >= data_min,
        db_models.ProcessedCostData.date <= data_max,
        db_models.ProcessedCostData.user_id == current_user.id,
    ).order_by(db_models.ProcessedCostData.date).all()
    total_cost = sum(c.total_cost for c in all_costs)
    num_days = (data_max - data_min).days or 1
    avg_daily = total_cost / num_days

    cost_change_pct = 0
    half = num_days // 2
    if half > 0 and len(all_costs) >= half:
        current_half = all_costs[-half:]
        prior_half = all_costs[:half]
        current_sum = sum(c.total_cost for c in current_half)
        prior_sum = sum(c.total_cost for c in prior_half)
        if prior_sum > 0:
            cost_change_pct = round(((current_sum - prior_sum) / prior_sum) * 100, 2)

    return schemas.APIResponse(
        status="success",
        data={
            "total_cost": round(total_cost, 2),
            "monthly_cost": round(avg_daily * 30, 2),
            "average_daily_cost": round(avg_daily, 2),
            "cost_change_pct": cost_change_pct,
        },
        message="Cost overview retrieved",
    )


@router.get("/summary", response_model=schemas.APIResponse)
async def get_cost_summary(
    days: Optional[int] = Query(None, ge=1, le=365),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Get cost summary.

    By default shows the full available date range.
    Pass `days` for a rolling window, or `start`/`end` for an exact range.
    """
    try:
        actual_start, actual_end = _resolve_date_range(db, current_user.id, days, start, end)
        if actual_end is None:
            return schemas.APIResponse(
                status="success",
                data={"message": "No cost data found in database"},
                message="Empty database"
            )

        costs = db.query(db_models.ProcessedCostData).filter(
            db_models.ProcessedCostData.date >= actual_start,
            db_models.ProcessedCostData.date <= actual_end,
            db_models.ProcessedCostData.user_id == current_user.id,
        ).all()

        if not costs:
            return schemas.APIResponse(
                status="success",
                data={"message": "No cost data found for specified period"},
                message="Empty period"
            )

        total_cost = sum(c.total_cost for c in costs)
        num_days = (actual_end - actual_start).days or 1
        avg_daily_cost = total_cost / num_days

        cost_change_pct = 0
        half_count = len(costs) // 2
        if half_count > 0:
            current_sum = sum(c.total_cost for c in costs[-half_count:])
            prior_sum = sum(c.total_cost for c in costs[:half_count])
            if prior_sum > 0:
                cost_change_pct = round(((current_sum - prior_sum) / prior_sum) * 100, 2)

        summary = {
            "total_cost": round(total_cost, 2),
            "monthly_cost": round(avg_daily_cost * 30, 2),
            "average_daily_cost": round(avg_daily_cost, 2),
            "cost_change_pct": cost_change_pct,
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
    days: Optional[int] = Query(None, ge=1, le=365),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    service: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Get cost time series data.

    By default shows the full available date range.
    Pass `days` for a rolling window, or `start`/`end` for an exact range.
    """
    try:
        actual_start, actual_end = _resolve_date_range(db, current_user.id, days, start, end)
        if actual_end is None:
            return schemas.APIResponse(
                status="success",
                data={"timeseries": []},
                message="No cost data found in database"
            )

        query = db.query(db_models.ProcessedCostData).filter(
            db_models.ProcessedCostData.date >= actual_start,
            db_models.ProcessedCostData.date <= actual_end,
            db_models.ProcessedCostData.user_id == current_user.id,
        )

        if service:
            query = query.filter(db_models.ProcessedCostData.service == service)
        if region:
            query = query.filter(db_models.ProcessedCostData.region == region)

        costs = query.order_by(db_models.ProcessedCostData.date).all()

        timeseries = [
            {
                "date": c.date.isoformat(),
                "cost": round(c.total_cost, 2)
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
    days: Optional[int] = Query(None, ge=1, le=365),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Get cost breakdown by service.

    By default shows the full available date range.
    Pass `days` for a rolling window, or `start`/`end` for an exact range.
    """
    try:
        actual_start, actual_end = _resolve_date_range(db, current_user.id, days, start, end)
        if actual_end is None:
            return schemas.APIResponse(
                status="success",
                data={"breakdown": []},
                message="No cost data found in database"
            )

        costs = db.query(db_models.ProcessedCostData).filter(
            db_models.ProcessedCostData.date >= actual_start,
            db_models.ProcessedCostData.date <= actual_end,
            db_models.ProcessedCostData.user_id == current_user.id,
        ).all()

        service_costs = {}
        for cost in costs:
            if cost.service not in service_costs:
                service_costs[cost.service] = 0
            service_costs[cost.service] += cost.total_cost

        total = sum(service_costs.values())

        breakdown = []
        for svc, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True):
            breakdown.append({
                "name": svc,
                "cost": round(cost, 2),
                "pct": round(calculate_percentage(cost, total), 2)
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
    days: Optional[int] = Query(None, ge=1, le=365),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Get cost breakdown by region.

    By default shows the full available date range.
    Pass `days` for a rolling window, or `start`/`end` for an exact range.
    """
    try:
        actual_start, actual_end = _resolve_date_range(db, current_user.id, days, start, end)
        if actual_end is None:
            return schemas.APIResponse(
                status="success",
                data={"breakdown": []},
                message="No cost data found in database"
            )

        costs = db.query(db_models.ProcessedCostData).filter(
            db_models.ProcessedCostData.date >= actual_start,
            db_models.ProcessedCostData.date <= actual_end,
            db_models.ProcessedCostData.user_id == current_user.id,
        ).all()

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
                "name": region,
                "cost": round(cost, 2),
                "pct": round(calculate_percentage(cost, total), 2)
            })

        return schemas.APIResponse(
            status="success",
            data={"breakdown": breakdown},
            message="Region breakdown retrieved"
        )
    except Exception as e:
        logger.error(f"Error getting region breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))
