"""
Prophet time series forecasting model for cost prediction.
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple
from prophet import Prophet
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class ProphetForecastingModel:
    """Prophet model for time series forecasting."""
    
    def __init__(self, interval_width: float = 0.95, yearly_seasonality: bool = False):
        """
        Initialize Prophet model.
        
        Args:
            interval_width: Prediction interval width (0-1)
            yearly_seasonality: Enable yearly seasonality
        """
        self.interval_width = interval_width
        self.yearly_seasonality = yearly_seasonality
        self.models: Dict[str, Prophet] = {}
        
    def prepare_data(self, df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
        """
        Prepare data in Prophet format.
        
        Args:
            df: Input dataframe
            date_col: Date column name
            value_col: Value column name
            
        Returns:
            DataFrame with 'ds' and 'y' columns
        """
        prepared = df[[date_col, value_col]].copy()
        prepared.columns = ['ds', 'y']
        prepared['ds'] = pd.to_datetime(prepared['ds'])
        prepared = prepared.sort_values('ds')
        return prepared
    
    def train(self, df: pd.DataFrame, date_col: str = 'ds', value_col: str = 'y', 
              model_name: str = 'default') -> None:
        """
        Train Prophet model on time series data.
        
        Args:
            df: Input dataframe
            date_col: Date column name
            value_col: Value column name
            model_name: Name to store this model
        """
        try:
            prepared_df = self.prepare_data(df, date_col, value_col)
            
            logger.info(f"Training Prophet model '{model_name}' with {len(prepared_df)} samples")
            
            model = Prophet(
                interval_width=self.interval_width,
                yearly_seasonality=self.yearly_seasonality,
                daily_seasonality=False,
                weekly_seasonality=True
            )
            
            model.fit(prepared_df)
            self.models[model_name] = model
            
            logger.info(f"Prophet model '{model_name}' training completed")
        except Exception as e:
            logger.error(f"Error training Prophet model: {e}")
            raise
    
    def forecast(self, periods: int = 30, model_name: str = 'default') -> pd.DataFrame:
        """
        Generate forecast for specified periods.
        
        Args:
            periods: Number of periods to forecast
            model_name: Name of trained model to use
            
        Returns:
            DataFrame with forecast results
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Available: {list(self.models.keys())}")
        
        try:
            model = self.models[model_name]
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)
            
            # Return only future predictions
            future_forecast = forecast[forecast['ds'] > forecast['ds'].iloc[-periods-1]][['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            
            return future_forecast
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            raise
    
    def get_forecast_components(self, model_name: str = 'default') -> Dict:
        """
        Get forecast components (trend, seasonality).
        
        Args:
            model_name: Name of trained model
            
        Returns:
            Dictionary with component information
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")
        
        model = self.models[model_name]
        return {
            'has_yearly': model.yearly_seasonality,
            'has_weekly': model.weekly_seasonality,
            'has_daily': model.daily_seasonality
        }
    
    def forecast_service_timeseries(self, df: pd.DataFrame, services: List[str], 
                                   periods: int = 30) -> Dict[str, pd.DataFrame]:
        """
        Forecast for multiple services.
        
        Args:
            df: Input dataframe with 'ds', 'y', and 'service' columns
            services: List of service names
            periods: Forecast periods
            
        Returns:
            Dictionary mapping service names to forecast dataframes
        """
        forecasts = {}
        
        for service in services:
            try:
                service_data = df[df['service'] == service][['ds', 'y']].copy()
                service_data.columns = ['ds', 'y']
                
                if len(service_data) < 3:
                    logger.warning(f"Insufficient data for service {service}")
                    continue
                
                model_name = f"service_{service}"
                self.train(service_data, model_name=model_name)
                forecast = self.forecast(periods=periods, model_name=model_name)
                forecast['service'] = service
                forecasts[service] = forecast
            except Exception as e:
                logger.error(f"Error forecasting for service {service}: {e}")
        
        return forecasts
