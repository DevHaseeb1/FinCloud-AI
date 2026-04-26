"""
Data preprocessing and ETL pipeline.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handle data cleaning and preprocessing."""
    
    @staticmethod
    def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Step 1: Clean raw data.
        
        Args:
            df: Raw input dataframe
            
        Returns:
            Cleaned dataframe
        """
        try:
            logger.info(f"Cleaning {len(df)} rows of raw data")
            df = df.copy()
            
            # Remove null values
            initial_rows = len(df)
            df = df.dropna(subset=['timestamp', 'service', 'cost'])
            logger.info(f"Removed {initial_rows - len(df)} rows with null values")
            
            # Fix invalid timestamps
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
            
            # Normalize service names (lowercase, strip whitespace)
            df['service'] = df['service'].str.lower().str.strip()
            df['region'] = df['region'].str.lower().str.strip()
            
            # Convert cost to float, handle invalid values
            df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
            df = df[df['cost'] >= 0]  # Remove negative costs
            
            # Convert usage_quantity to float
            if 'usage_quantity' in df.columns:
                df['usage_quantity'] = pd.to_numeric(df['usage_quantity'], errors='coerce')
            
            logger.info(f"Cleaned data: {len(df)} rows remaining")
            return df
        except Exception as e:
            logger.error(f"Error in data cleaning: {e}")
            raise
    
    @staticmethod
    def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
        """
        Step 2: Feature engineering.
        
        Args:
            df: Cleaned dataframe
            
        Returns:
            Dataframe with engineered features
        """
        try:
            logger.info("Performing feature engineering")
            df = df.copy()
            df = df.sort_values('timestamp')
            
            # Extract date components
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            
            # Create daily_cost and hourly_cost
            df['daily_cost'] = df['cost']  # Will be aggregated
            df['hourly_cost'] = df['cost'] / 24  # Estimate hourly from daily
            
            # Cost velocity (rate of change)
            df['cost_velocity'] = df['cost'].diff().fillna(0)
            
            # Rolling averages (per service + region)
            df = df.sort_values('timestamp')
            for service in df['service'].unique():
                for region in df[df['service'] == service]['region'].unique():
                    mask = (df['service'] == service) & (df['region'] == region)
                    df.loc[mask, 'rolling_avg_7d'] = df.loc[mask, 'cost'].rolling(
                        window=7, min_periods=1
                    ).mean()
                    df.loc[mask, 'rolling_avg_30d'] = df.loc[mask, 'cost'].rolling(
                        window=30, min_periods=1
                    ).mean()
            
            logger.info("Feature engineering completed")
            return df
        except Exception as e:
            logger.error(f"Error in feature engineering: {e}")
            raise
    
    @staticmethod
    def aggregate_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Step 3: Aggregate data by date, service, region.
        
        Args:
            df: Feature-engineered dataframe
            
        Returns:
            Aggregated dataframe
        """
        try:
            logger.info("Aggregating data by date, service, region")
            
            df = df.copy()
            df['date'] = pd.to_datetime(df['date'])
            
            # Aggregate
            agg_df = df.groupby(['date', 'service', 'region']).agg({
                'cost': 'sum',
                'daily_cost': 'sum',
                'hourly_cost': 'sum',
                'rolling_avg_7d': 'mean',
                'rolling_avg_30d': 'mean',
                'cost_velocity': 'mean',
                'usage_quantity': 'sum' if 'usage_quantity' in df.columns else 'first'
            }).reset_index()
            
            agg_df.rename(columns={'cost': 'total_cost'}, inplace=True)
            
            logger.info(f"Aggregated data: {len(agg_df)} rows")
            return agg_df
        except Exception as e:
            logger.error(f"Error in data aggregation: {e}")
            raise
    
    @staticmethod
    def full_preprocessing_pipeline(df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute complete preprocessing pipeline.
        
        Args:
            df: Raw input dataframe
            
        Returns:
            Processed dataframe ready for storage
        """
        try:
            logger.info("Starting preprocessing pipeline")
            
            # Step 1: Clean
            df = DataPreprocessor.clean_raw_data(df)
            
            # Step 2: Feature engineering
            df = DataPreprocessor.feature_engineering(df)
            
            # Step 3: Aggregate
            df = DataPreprocessor.aggregate_data(df)
            
            logger.info("Preprocessing pipeline completed")
            return df
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {e}")
            raise


class DataValidator:
    """Validate data quality."""
    
    @staticmethod
    def validate_cost_data(df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate cost data quality.
        
        Args:
            df: Input dataframe
            
        Returns:
            Tuple of (is_valid, message)
        """
        if df is None or len(df) == 0:
            return False, "Empty dataframe"
        
        required_columns = ['timestamp', 'service', 'region', 'cost']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            return False, f"Missing columns: {missing_cols}"
        
        # Check for invalid costs
        if (df['cost'] < 0).any():
            return False, "Negative costs found"
        
        # Check timestamps
        if df['timestamp'].isna().any():
            return False, "Invalid timestamps found"
        
        return True, "Data validation passed"
