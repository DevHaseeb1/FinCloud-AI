"""
Helper utilities and common functions.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# backend/app/utils/helpers.py — add this function

from sqlalchemy.orm import Session
from sqlalchemy import func

def get_table_date_range(db: Session, model, date_column_name: str = "date"):
    """Get actual min/max date from any model's date column."""
    date_col = getattr(model, date_column_name)
    result = db.query(func.min(date_col), func.max(date_col)).first()
    return result[0], result[1]  # (min_date, max_date) — both None if table is empty

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        
    Returns:
        Logger instance
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def generate_sample_cost_data(num_records: int = 1000, 
                             num_days: int = 30) -> pd.DataFrame:
    """
    Generate sample AWS cost data for testing.
    
    Args:
        num_records: Number of records to generate
        num_days: Number of days in dataset
        
    Returns:
        Sample dataframe
    """
    services = ['ec2', 's3', 'lambda', 'rds', 'dynamodb', 'cloudfront']
    regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
    
    records = []
    start_date = datetime.now() - timedelta(days=num_days)
    
    for _ in range(num_records):
        timestamp = start_date + timedelta(
            days=np.random.randint(0, num_days),
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )
        
        service = np.random.choice(services)
        region = np.random.choice(regions)
        
        # Generate realistic costs
        base_cost = np.random.uniform(10, 1000)
        # Add some anomalies
        if np.random.random() < 0.1:
            cost = base_cost * np.random.uniform(2, 5)
        else:
            cost = base_cost
        
        records.append({
            'timestamp': timestamp,
            'service': service,
            'region': region,
            'cost': cost,
            'usage_quantity': np.random.uniform(100, 10000),
            'instance_type': f't{np.random.choice([2, 3])}.' + np.random.choice(['micro', 'small', 'medium']),
            'account_id': f'12345678{np.random.randint(0, 100):02d}'
        })
    
    df = pd.DataFrame(records)
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    logger.info(f"Generated {len(df)} sample cost records")
    return df


def format_currency(value: float) -> str:
    """
    Format value as currency.
    
    Args:
        value: Numeric value
        
    Returns:
        Formatted currency string
    """
    return f"${value:,.2f}"


def calculate_percentage(value: float, total: float) -> float:
    """
    Calculate percentage.
    
    Args:
        value: Numerator
        total: Denominator
        
    Returns:
        Percentage
    """
    return (value / total * 100) if total > 0 else 0


def get_trend(current: float, previous: float) -> str:
    """
    Determine cost trend.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        Trend direction: 'up', 'down', or 'stable'
    """
    if previous == 0:
        return 'stable'
    
    change_pct = ((current - previous) / abs(previous)) * 100
    
    if change_pct > 5:
        return 'up'
    elif change_pct < -5:
        return 'down'
    else:
        return 'stable'


def aggregate_by_service(df: pd.DataFrame) -> Dict[str, float]:
    """
    Aggregate costs by service.
    
    Args:
        df: Input dataframe with 'service' and 'total_cost' columns
        
    Returns:
        Dictionary mapping service to total cost
    """
    if 'service' not in df.columns or 'total_cost' not in df.columns:
        raise ValueError("Dataframe must have 'service' and 'total_cost' columns")
    
    return df.groupby('service')['total_cost'].sum().to_dict()


def aggregate_by_region(df: pd.DataFrame) -> Dict[str, float]:
    """
    Aggregate costs by region.
    
    Args:
        df: Input dataframe with 'region' and 'total_cost' columns
        
    Returns:
        Dictionary mapping region to total cost
    """
    if 'region' not in df.columns or 'total_cost' not in df.columns:
        raise ValueError("Dataframe must have 'region' and 'total_cost' columns")
    
    return df.groupby('region')['total_cost'].sum().to_dict()


def datetime_to_iso(dt: datetime) -> str:
    """
    Convert datetime to ISO format string.
    
    Args:
        dt: Datetime object
        
    Returns:
        ISO format string
    """
    return dt.isoformat()
