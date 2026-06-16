"""
Configuration file for FinCloud-AI Backend.
Additional settings and constants.
"""

import os
from enum import Enum
from typing import List

# API Configuration
API_VERSION = "v1"
API_TITLE = "FinCloud-AI Backend API"
API_DESCRIPTION = "Production-grade FinOps platform for cloud cost optimization"

# Service Names
SERVICES = [
    'ec2',
    's3',
    'lambda',
    'rds',
    'dynamodb',
    'cloudfront',
    'elasticache',
    'opensearch',
    'kinesis',
    'sqs',
    'sns',
    'codebuild',
    'codecommit',
    'athena',
    'glue'
]

# AWS Regions
AWS_REGIONS = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'eu-west-1',
    'eu-central-1',
    'ap-southeast-1',
    'ap-northeast-1',
    'ca-central-1'
]

# ML Model Parameters
class MLConfig:
    """ML Model configuration."""
    
    # Isolation Forest (Anomaly Detection)
    ANOMALY_CONTAMINATION = float(os.getenv('ANOMALY_CONTAMINATION', 0.05))
    ANOMALY_N_ESTIMATORS = 100
    ANOMALY_RANDOM_STATE = 42
    
    # Prophet (Forecasting)
    FORECAST_PERIODS = int(os.getenv('FORECAST_PERIODS', 30))
    FORECAST_INTERVAL_WIDTH = float(os.getenv('FORECAST_INTERVAL_WIDTH', 0.95))
    FORECAST_YEARLY_SEASONALITY = False
    
    # Random Forest (Optimization)
    OPTIMIZATION_N_ESTIMATORS = 100
    OPTIMIZATION_MAX_DEPTH = 15
    OPTIMIZATION_RANDOM_STATE = 42


class RecommendationType(str, Enum):
    """Cost optimization recommendation types."""
    
    COST_CONSOLIDATION = "cost_consolidation"
    RIGHT_SIZING = "right_sizing"
    RESERVED_CAPACITY = "reserved_capacity"
    SPOT_INSTANCES = "spot_instances"
    UNUSED_RESOURCES = "unused_resources"
    AUTOSCALING = "autoscaling"


class AnomalyExplanation(str, Enum):
    """Anomaly explanations."""
    
    SEVERE = "Severe anomaly detected in costs"
    SIGNIFICANT = "Significant cost spike detected"
    MINOR = "Minor anomaly in costs"
    NORMAL = "Normal cost pattern"


# Pagination
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000

# File Upload
MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', 100))
ALLOWED_FILE_EXTENSIONS = ['csv', 'xlsx']

# Caching
CACHE_TTL_SECONDS = 300  # 5 minutes
CACHE_COST_SUMMARY = True
CACHE_FORECASTS = True

# Feature Engineering
ROLLING_WINDOW_7D = 7
ROLLING_WINDOW_30D = 30

# Anomaly Detection Thresholds
ANOMALY_SCORE_THRESHOLD_LOW = 0.5
ANOMALY_SCORE_THRESHOLD_MEDIUM = 0.7
ANOMALY_SCORE_THRESHOLD_HIGH = 0.85

# AWS Integration
AWS_COST_EXPLORER_GRANULARITY = "DAILY"
AWS_COST_EXPLORER_DEFAULT_DAYS = 90
AWS_CUR_DEFAULT_DAYS = 30
AWS_FETCH_TIMEOUT_SECONDS = 120
AWS_CREDENTIAL_ENCRYPTION_KEY_ENV = "AWS_CREDENTIAL_ENCRYPTION_KEY"
