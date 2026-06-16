"""
SQLAlchemy database models.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class User(Base):
    """Application user for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="user")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class RawCostData(Base):
    """Raw AWS billing data before preprocessing."""
    
    __tablename__ = "raw_cost_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    service = Column(String(100), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    cost = Column(Float, nullable=False)
    usage_quantity = Column(Float, nullable=True)
    instance_type = Column(String(100), nullable=True)
    account_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ProcessedCostData(Base):
    """Cleaned and preprocessed cost data."""
    
    __tablename__ = "processed_cost_data"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    service = Column(String(100), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    total_cost = Column(Float, nullable=False)
    daily_cost = Column(Float, nullable=True)
    hourly_cost = Column(Float, nullable=True)
    rolling_avg_7d = Column(Float, nullable=True)
    rolling_avg_30d = Column(Float, nullable=True)
    cost_velocity = Column(Float, nullable=True)
    usage_quantity = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Anomaly(Base):
    """Detected cost anomalies."""
    
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    service = Column(String(100), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    anomaly_score = Column(Float, nullable=False)
    anomaly_flag = Column(Boolean, nullable=False, default=False)
    cost_value = Column(Float, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Forecast(Base):
    """Cost forecasts using Prophet model."""
    
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    service = Column(String(100), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    predicted_cost = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Recommendation(Base):
    """Cost optimization recommendations."""
    
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(100), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    recommendation_type = Column(String(100), nullable=False)
    suggestion = Column(Text, nullable=False)
    estimated_savings = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class AwsConnection(Base):
    """Stores AWS account connections."""
    
    __tablename__ = "aws_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    account_id = Column(String(100), nullable=True, index=True)
    role_arn = Column(String(500), nullable=True)
    external_id = Column(String(200), nullable=True)
    external_id_expires_at = Column(DateTime, nullable=True)
    access_key_encrypted = Column(Text, nullable=True)
    secret_key_encrypted = Column(Text, nullable=True)
    region = Column(String(50), nullable=False, default="us-east-1")
    s3_cur_bucket = Column(String(255), nullable=True)
    s3_cur_prefix = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    last_fetch_at = Column(DateTime, nullable=True)
    last_fetch_status = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AwsFetchHistory(Base):
    """Tracks fetch operations for AWS connections."""

    __tablename__ = "aws_fetch_history"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, nullable=False, index=True)
    source = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    rows_fetched = Column(Integer, default=0)
    rows_processed = Column(Integer, default=0)
    duration_seconds = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
