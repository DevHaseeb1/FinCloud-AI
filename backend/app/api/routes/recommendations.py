"""
Cost optimization recommendations API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models import db_models, schemas
from app.api.dependencies import require_authenticated_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=schemas.APIResponse)
async def get_recommendations(
    min_confidence: float = Query(0.6, ge=0, le=1),
    priority: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: None = Depends(require_authenticated_user),
):
    """
    Get cost optimization recommendations.
    
    Args:
        min_confidence: Minimum confidence score
        priority: Filter by priority level
        skip: Pagination offset
        limit: Pagination limit
        db: Database session
        
    Returns:
        List of recommendations
    """
    try:
        query = db.query(db_models.Recommendation).filter(
            db_models.Recommendation.confidence_score >= min_confidence
        )
        
        if priority is not None:
            query = query.filter(db_models.Recommendation.priority == priority)
        
        recommendations = query.order_by(
            db_models.Recommendation.estimated_savings.desc()
        ).offset(skip).limit(limit).all()
        
        total_count = query.count()
        
        total_potential_savings = sum(r.estimated_savings for r in recommendations)
        
        rec_data = [
            {
                "id": r.id,
                "service": r.service,
                "region": r.region,
                "recommendation_type": r.recommendation_type,
                "suggestion": r.suggestion,
                "estimated_savings": round(r.estimated_savings, 2),
                "confidence_score": round(r.confidence_score, 4),
                "priority": r.priority,
                "created_at": r.created_at.isoformat()
            }
            for r in recommendations
        ]
        
        return schemas.APIResponse(
            status="success",
            data={
                "recommendations": rec_data,
                "total_count": total_count,
                "returned_count": len(rec_data),
                "total_potential_savings": round(total_potential_savings, 2)
            },
            message=f"Retrieved {len(rec_data)} recommendations"
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/high-priority", response_model=schemas.APIResponse)
async def get_high_priority_recommendations(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: None = Depends(require_authenticated_user),
):
    """
    Get high-priority recommendations.
    
    Args:
        limit: Number of recommendations
        db: Database session
        
    Returns:
        High-priority recommendations
    """
    try:
        recommendations = db.query(db_models.Recommendation).filter(
            db_models.Recommendation.priority == 1
        ).order_by(
            db_models.Recommendation.estimated_savings.desc()
        ).limit(limit).all()
        
        total_savings = sum(r.estimated_savings for r in recommendations)
        
        rec_data = [
            {
                "id": r.id,
                "service": r.service,
                "region": r.region,
                "recommendation_type": r.recommendation_type,
                "suggestion": r.suggestion,
                "estimated_savings": round(r.estimated_savings, 2),
                "confidence_score": round(r.confidence_score, 4),
                "priority": r.priority
            }
            for r in recommendations
        ]
        
        return schemas.APIResponse(
            status="success",
            data={
                "recommendations": rec_data,
                "total_potential_savings": round(total_savings, 2)
            },
            message=f"Retrieved {len(rec_data)} high-priority recommendations"
        )
    except Exception as e:
        logger.error(f"Error getting high-priority recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-service", response_model=schemas.APIResponse)
async def get_recommendations_by_service(
    service: str = Query(...),
    db: Session = Depends(get_db),
    _: None = Depends(require_authenticated_user),
):
    """
    Get recommendations for specific service.
    
    Args:
        service: Service name
        db: Database session
        
    Returns:
        Service recommendations
    """
    try:
        recommendations = db.query(db_models.Recommendation).filter(
            db_models.Recommendation.service == service
        ).order_by(
            db_models.Recommendation.estimated_savings.desc()
        ).all()
        
        total_savings = sum(r.estimated_savings for r in recommendations)
        
        rec_data = [
            {
                "id": r.id,
                "region": r.region,
                "recommendation_type": r.recommendation_type,
                "suggestion": r.suggestion,
                "estimated_savings": round(r.estimated_savings, 2),
                "confidence_score": round(r.confidence_score, 4),
                "priority": r.priority
            }
            for r in recommendations
        ]
        
        return schemas.APIResponse(
            status="success",
            data={
                "service": service,
                "recommendations": rec_data,
                "total_potential_savings": round(total_savings, 2)
            },
            message=f"Retrieved {len(rec_data)} recommendations for {service}"
        )
    except Exception as e:
        logger.error(f"Error getting service recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=schemas.APIResponse)
async def get_recommendations_summary(
    db: Session = Depends(get_db),
    _: None = Depends(require_authenticated_user),
):
    """
    Get recommendations summary.
    
    Returns:
        Recommendations summary
    """
    try:
        all_recs = db.query(db_models.Recommendation).all()
        
        total_savings = sum(r.estimated_savings for r in all_recs)
        by_priority = {}
        by_type = {}
        
        for rec in all_recs:
            priority = rec.priority
            rec_type = rec.recommendation_type
            
            if priority not in by_priority:
                by_priority[priority] = 0
            by_priority[priority] += 1
            
            if rec_type not in by_type:
                by_type[rec_type] = 0
            by_type[rec_type] += 1
        
        summary = {
            "total_recommendations": len(all_recs),
            "total_potential_savings": round(total_savings, 2),
            "by_priority": by_priority,
            "by_type": by_type
        }
        
        return schemas.APIResponse(
            status="success",
            data=summary,
            message="Recommendations summary retrieved"
        )
    except Exception as e:
        logger.error(f"Error getting recommendations summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
