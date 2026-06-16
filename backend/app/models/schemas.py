"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re


# Auth Schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: str
    password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v):
            raise ValueError("Invalid email format")
        return v


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


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


# AWS Connection Schemas
class AwsConnectionCreate(BaseModel):
    """Schema for creating an AWS connection."""
    name: str
    account_id: Optional[str] = None
    role_arn: Optional[str] = None
    external_id: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region: str = "us-east-1"
    s3_cur_bucket: Optional[str] = None
    s3_cur_prefix: Optional[str] = None


class AwsConnectionUpdate(BaseModel):
    """Schema for updating an AWS connection."""
    name: Optional[str] = None
    account_id: Optional[str] = None
    role_arn: Optional[str] = None
    external_id: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region: Optional[str] = None
    s3_cur_bucket: Optional[str] = None
    s3_cur_prefix: Optional[str] = None
    is_active: Optional[bool] = None


class AwsConnectionResponse(BaseModel):
    """Schema for AWS connection response."""
    id: int
    name: str
    account_id: Optional[str] = None
    role_arn: Optional[str] = None
    region: str
    s3_cur_bucket: Optional[str] = None
    s3_cur_prefix: Optional[str] = None
    is_active: bool
    last_fetch_at: Optional[datetime] = None
    last_fetch_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_validator("role_arn", mode="before")
    @classmethod
    def decrypt_role_arn(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        from app.core.aws_auth import decrypt_credential
        try:
            return decrypt_credential(v)
        except Exception:
            return v

    class Config:
        from_attributes = True


class AwsConnectionSetupResponse(BaseModel):
    """Schema for AWS connection setup response."""
    external_id: str
    role_name: str
    cloudformation_url: str


class AwsTestRequest(BaseModel):
    """Schema for testing an AWS connection."""
    connection_id: int
    role_arn: Optional[str] = None
    external_id: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region: str = "us-east-1"
    s3_cur_bucket: Optional[str] = None
    s3_cur_prefix: Optional[str] = None


class AwsTestResult(BaseModel):
    """Schema for a single validation check result."""
    check: str
    status: str
    message: Optional[str] = None


class AwsTestResponse(BaseModel):
    """Schema for AWS connection test response."""
    connection_id: int
    overall_status: str
    checks: list[AwsTestResult]


class AwsFetchRequest(BaseModel):
    """Schema for triggering an AWS data fetch."""
    connection_id: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    use_cur: bool = False


class AwsFetchResponse(BaseModel):
    """Schema for AWS data fetch response."""
    connection_id: int
    status: str
    rows_fetched: int
    rows_ingested: int
    message: str


class AwsFetchHistoryResponse(BaseModel):
    """Schema for fetch history record."""
    id: int
    connection_id: int
    source: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    rows_fetched: int
    rows_processed: int
    duration_seconds: Optional[float] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
