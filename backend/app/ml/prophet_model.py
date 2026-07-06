"""
Prophet time series forecasting model for cost prediction.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class ProphetForecastingModel:
    def __init__(self, interval_width: float = 0.95, yearly_seasonality: bool = False):
        self.interval_width = interval_width
        self.yearly_seasonality = yearly_seasonality
        self.models: Dict[str, Prophet] = {}
        self.model_info: Dict[str, Dict] = {}
        self.trained_models: Dict[str, bool] = {}

    def _add_regressors(self, model: Prophet) -> Prophet:
        model.add_regressor('day_of_week')
        model.add_regressor('is_month_start')
        model.add_regressor('is_month_end')
        return model

    def _future_regressors(self, future: pd.DataFrame, last_date: pd.Timestamp) -> pd.DataFrame:
        future['day_of_week'] = future['ds'].dt.dayofweek
        future['is_month_start'] = (future['ds'].dt.day <= 3).astype(int)
        future['is_month_end'] = (future['ds'].dt.day >= 28).astype(int)
        return future

    def _prepare_data(self, df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
        prepared = df[[date_col, value_col]].copy()
        prepared.columns = ['ds', 'y']
        prepared['ds'] = pd.to_datetime(prepared['ds']).dt.tz_localize(None)
        prepared = prepared.sort_values('ds')
        prepared['y'] = np.log1p(np.maximum(prepared['y'], 0))

        prepared['day_of_week'] = prepared['ds'].dt.dayofweek
        prepared['is_month_start'] = (prepared['ds'].dt.day <= 3).astype(int)
        prepared['is_month_end'] = (prepared['ds'].dt.day >= 28).astype(int)

        return prepared

    def _tune_changepoint(self, df: pd.DataFrame) -> float:
        n = len(df)
        if n < 30:
            return 0.05

        horizon_days = min(30, max(7, n // 5))
        initial_days = n - horizon_days - 7
        if initial_days < 14:
            return 0.05

        initial_str = f'{initial_days} days'
        period_str = f'{max(7, horizon_days // 2)} days'
        horizon_str = f'{horizon_days} days'

        best_mape = float('inf')
        best_cp = 0.05

        for cp in [0.001, 0.01, 0.05, 0.1, 0.5]:
            try:
                m = Prophet(
                    interval_width=self.interval_width,
                    yearly_seasonality=self.yearly_seasonality,
                    weekly_seasonality=True,
                    daily_seasonality=False,
                    changepoint_prior_scale=cp,
                )
                m = self._add_regressors(m)
                m.fit(df)

                cv_results = cross_validation(
                    m, initial=initial_str, period=period_str, horizon=horizon_str,
                    disable_tqdm=True
                )
                perf = performance_metrics(cv_results, rolling_window=1)
                mape = perf['mape'].iloc[-1]

                if mape < best_mape:
                    best_mape = mape
                    best_cp = cp
            except Exception as e:
                logger.warning(f"Changepoint tuning failed for cp={cp}: {e}")
                continue

        logger.info(f"Best changepoint_prior_scale={best_cp} (MAPE={best_mape:.4f})")
        return best_cp

    def train(self, df: pd.DataFrame, date_col: str = 'ds', value_col: str = 'y',
              model_name: str = 'default', tune: bool = False) -> None:
        try:
            prepared_df = self._prepare_data(df, date_col, value_col)

            logger.info(f"Training Prophet model '{model_name}' with {len(prepared_df)} samples")

            changepoint = self._tune_changepoint(prepared_df) if tune else 0.05

            model = Prophet(
                interval_width=self.interval_width,
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=changepoint,
                uncertainty_samples=300,
            )

            model = self._add_regressors(model)
            model.fit(prepared_df)

            self.models[model_name] = model
            self.model_info[model_name] = {
                'changepoint_prior_scale': changepoint,
                'n_samples': len(prepared_df),
            }
            self.trained_models[model_name] = True

            logger.info(f"Prophet model '{model_name}' training completed (cp={changepoint})")
        except Exception as e:
            logger.error(f"Error training Prophet model: {e}")
            raise

    def forecast(self, periods: int = 30, model_name: str = 'default') -> pd.DataFrame:
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Available: {list(self.models.keys())}")

        try:
            model = self.models[model_name]
            future = model.make_future_dataframe(periods=periods)
            future = self._future_regressors(future, future['ds'].max())

            forecast = model.predict(future)

            future_forecast = forecast[forecast['ds'] > forecast['ds'].iloc[-periods-1]].copy()

            result = pd.DataFrame({
                'ds': future_forecast['ds'],
                'yhat': np.expm1(future_forecast['yhat']),
                'yhat_lower': np.expm1(np.maximum(future_forecast['yhat_lower'], 0)),
                'yhat_upper': np.expm1(np.maximum(future_forecast['yhat_upper'], 0)),
            })

            result['trend'] = np.expm1(np.maximum(future_forecast['trend'], 0))
            result['weekly'] = future_forecast['weekly'].values
            result['weekly_lower'] = future_forecast['weekly_lower'].values
            result['weekly_upper'] = future_forecast['weekly_upper'].values
            result['multiplicative_terms'] = future_forecast['multiplicative_terms'].values

            return result
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            raise

    def get_forecast_components(self, model_name: str = 'default') -> Dict:
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")

        model = self.models[model_name]
        return {
            'has_yearly': model.yearly_seasonality,
            'has_weekly': model.weekly_seasonality,
            'has_daily': model.daily_seasonality,
        }

    def forecast_service_timeseries(self, df: pd.DataFrame, services: List[str],
                                   periods: int = 30) -> Dict[str, pd.DataFrame]:
        forecasts = {}

        for service in services:
            try:
                service_data = df[df['service'] == service][['ds', 'y']].copy()
                service_data.columns = ['ds', 'y']

                if len(service_data) < 3:
                    logger.warning(f"Insufficient data for service {service}")
                    continue

                if len(service_data) < 14:
                    avg = service_data['y'].mean()
                    std = service_data['y'].std()
                    last_date = service_data['ds'].max()
                    fallback = pd.DataFrame({
                        'ds': pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods),
                        'yhat': np.full(periods, avg),
                        'yhat_lower': np.full(periods, max(0, avg - 0.5 * std)),
                        'yhat_upper': np.full(periods, avg + 0.5 * std),
                        'trend': np.full(periods, avg),
                        'weekly': np.zeros(periods),
                        'weekly_lower': np.zeros(periods),
                        'weekly_upper': np.zeros(periods),
                        'multiplicative_terms': np.zeros(periods),
                    })
                    fallback['service'] = service
                    forecasts[service] = fallback
                    logger.info(f"Fallback forecast for {service} ({len(service_data)} samples)")
                    continue

                model_name = f"service_{service}"
                self.train(service_data, model_name=model_name, tune=False)
                forecast = self.forecast(periods=periods, model_name=model_name)
                forecast['service'] = service
                forecasts[service] = forecast
            except Exception as e:
                logger.error(f"Error forecasting for service {service}: {e}")

        return forecasts
