"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# Raw Cost Data Schemas
class RawCostDataBase(BaseModel):
    """Base schema for raw cost data."""
    timestamp: datetime
    service: str
    region: str
    cost: float
    usage_quantity: Optional[float] = None
    instance_type: Optional[str] = None
    account_id: Optional[str] = None


class RawCostDataCreate(RawCostDataBase):
    """Schema for creating raw cost data."""
    pass


class RawCostDataResponse(RawCostDataBase):
    """Schema for raw cost data response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Processed Cost Data Schemas
class ProcessedCostDataBase(BaseModel):
    """Base schema for processed cost data."""
    date: datetime
    service: str
    region: str
    total_cost: float
    daily_cost: Optional[float] = None
    hourly_cost: Optional[float] = None
    rolling_avg_7d: Optional[float] = None
    rolling_avg_30d: Optional[float] = None
    cost_velocity: Optional[float] = None
    usage_quantity: Optional[float] = None


class ProcessedCostDataResponse(ProcessedCostDataBase):
    """Schema for processed cost data response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Anomaly Schemas
class AnomalyBase(BaseModel):
    """Base schema for anomalies."""
    date: datetime
    service: str
    region: str
    anomaly_score: float
    anomaly_flag: bool
    cost_value: float
    explanation: Optional[str] = None


class AnomalyResponse(AnomalyBase):
    """Schema for anomaly response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Forecast Schemas
class ForecastBase(BaseModel):
    """Base schema for forecasts."""
    date: datetime
    service: str
    region: str
    predicted_cost: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(ForecastBase):
    """Schema for forecast response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Recommendation Schemas
class RecommendationBase(BaseModel):
    """Base schema for recommendations."""
    service: str
    region: str
    recommendation_type: str
    suggestion: str
    estimated_savings: float
    confidence_score: float
    priority: int = 0


class RecommendationResponse(RecommendationBase):
    """Schema for recommendation response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# API Response Schemas
class APIResponse(BaseModel):
    """Standard API response wrapper."""
    status: str = Field(..., description="Response status: success or error")
    data: Optional[dict] = Field(default=None, description="Response data")
    message: Optional[str] = Field(default="", description="Response message")


class CostSummaryResponse(BaseModel):
    """Cost summary response."""
    total_cost: float
    average_daily_cost: float
    highest_service: str
    highest_service_cost: float
    lowest_service: str
    lowest_service_cost: float
    period_start: datetime
    period_end: datetime


class TimeSeriesPoint(BaseModel):
    """Single time series data point."""
    timestamp: datetime
    value: float
    service: str
    region: str


class ServiceBreakdownResponse(BaseModel):
    """Service cost breakdown."""
    service: str
    total_cost: float
    percentage: float
    trend: str  # "up", "down", "stable"


class RegionBreakdownResponse(BaseModel):
    """Region cost breakdown."""
    region: str
    total_cost: float
    percentage: float
    services_count: int


class UploadResponse(BaseModel):
    """File upload response."""
    filename: str
    rows_uploaded: int
    rows_processed: int
    status: str


class PaginationParams(BaseModel):
    """Pagination parameters."""
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
