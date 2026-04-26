"""
Forecasting service using Prophet model.
"""

import pandas as pd
import logging
from app.ml.prophet_model import ProphetForecastingModel
from typing import Dict, List

logger = logging.getLogger(__name__)


class ForecastingService:
    """Service for cost forecasting."""
    
    def __init__(self, forecast_periods: int = 30, interval_width: float = 0.95):
        """
        Initialize forecasting service.
        
        Args:
            forecast_periods: Number of periods to forecast
            interval_width: Prediction interval width
        """
        self.forecast_periods = forecast_periods
        self.model = ProphetForecastingModel(interval_width=interval_width)
        self.is_trained = False
    
    def train(self, df: pd.DataFrame, service: str = 'all') -> None:
        """
        Train Prophet model.
        
        Args:
            df: Training dataframe with 'date' and 'total_cost' columns
            service: Service name or 'all' for aggregate
        """
        try:
            if service == 'all':
                # Aggregate all services
                train_df = df.groupby('date').agg({'total_cost': 'sum'}).reset_index()
                train_df.columns = ['ds', 'y']
                self.model.train(train_df, model_name='total')
            else:
                # Train for specific service
                train_df = df[df['service'] == service].copy()
                train_df = train_df.groupby('date').agg({'total_cost': 'sum'}).reset_index()
                train_df.columns = ['ds', 'y']
                self.model.train(train_df, model_name=service)
            
            self.is_trained = True
            logger.info(f"Forecasting model trained for {service}")
        except Exception as e:
            logger.error(f"Error training forecasting model: {e}")
            raise
    
    def forecast_total_cost(self) -> pd.DataFrame:
        """
        Forecast total cost for all services.
        
        Returns:
            Forecast dataframe
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        try:
            forecast = self.model.forecast(periods=self.forecast_periods, model_name='total')
            forecast.columns = ['date', 'predicted_cost', 'lower_bound', 'upper_bound']
            logger.info(f"Generated forecast for {len(forecast)} periods")
            return forecast
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            raise
    
    def forecast_by_service(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Forecast cost by service.
        
        Args:
            df: Training dataframe
            
        Returns:
            Dictionary mapping service names to forecasts
        """
        try:
            services = df['service'].unique()
            forecasts = {}
            
            for service in services:
                try:
                    self.train(df, service=service)
                    forecast = self.model.forecast(
                        periods=self.forecast_periods,
                        model_name=service
                    )
                    forecast.columns = ['date', 'predicted_cost', 'lower_bound', 'upper_bound']
                    forecast['service'] = service
                    forecasts[service] = forecast
                except Exception as e:
                    logger.warning(f"Could not forecast for service {service}: {e}")
            
            return forecasts
        except Exception as e:
            logger.error(f"Error in service forecasting: {e}")
            raise
    
    def get_forecast_summary(self, forecast_df: pd.DataFrame) -> Dict:
        """
        Get summary statistics from forecast.
        
        Args:
            forecast_df: Forecast dataframe
            
        Returns:
            Summary dictionary
        """
        return {
            'avg_predicted_cost': forecast_df['predicted_cost'].mean(),
            'max_predicted_cost': forecast_df['predicted_cost'].max(),
            'min_predicted_cost': forecast_df['predicted_cost'].min(),
            'total_predicted_cost': forecast_df['predicted_cost'].sum(),
            'forecast_start': forecast_df['date'].min(),
            'forecast_end': forecast_df['date'].max(),
            'confidence_interval': 'upper_bound - lower_bound'
        }
