"""
SQLAlchemy database models.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


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
