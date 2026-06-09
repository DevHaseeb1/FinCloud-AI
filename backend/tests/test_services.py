"""
Unit tests for FinCloud-AI Backend.
Run: pytest
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from app.api.routes.upload import map_aws_billing_columns
from app.services.preprocessing import DataPreprocessor, DataValidator
from app.ml.isolation_forest import IsolationForestModel
from app.ml.prophet_model import ProphetForecastingModel
from app.ml.random_forest import RandomForestOptimizer


class TestDataPreprocessor:
    """Test data preprocessing."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
            'service': ['ec2', 's3'] * 50,
            'region': ['us-east-1', 'us-west-2'] * 50,
            'cost': np.random.uniform(10, 1000, 100),
            'usage_quantity': np.random.uniform(100, 10000, 100)
        })
    
    def test_clean_raw_data(self, sample_data):
        """Test data cleaning."""
        cleaned = DataPreprocessor.clean_raw_data(sample_data)
        
        assert len(cleaned) > 0
        assert cleaned['cost'].isna().sum() == 0
        assert (cleaned['cost'] >= 0).all()
    
    def test_feature_engineering(self, sample_data):
        """Test feature engineering."""
        cleaned = DataPreprocessor.clean_raw_data(sample_data)
        engineered = DataPreprocessor.feature_engineering(cleaned)
        
        assert 'rolling_avg_7d' in engineered.columns
        assert 'rolling_avg_30d' in engineered.columns
        assert 'cost_velocity' in engineered.columns
    
    def test_full_pipeline(self, sample_data):
        """Test full preprocessing pipeline."""
        processed = DataPreprocessor.full_preprocessing_pipeline(sample_data)
        
        assert len(processed) > 0
        assert 'total_cost' in processed.columns
        assert 'date' in processed.columns


class TestDataValidator:
    """Test data validation."""
    
    def test_valid_data(self):
        """Test validation of valid data."""
        df = pd.DataFrame({
            'timestamp': [datetime.now()],
            'service': ['ec2'],
            'region': ['us-east-1'],
            'cost': [100.0]
        })
        
        is_valid, message = DataValidator.validate_cost_data(df)
        assert is_valid is True
    
    def test_missing_columns(self):
        """Test validation with missing columns."""
        df = pd.DataFrame({
            'timestamp': [datetime.now()],
            'service': ['ec2']
        })
        
        is_valid, message = DataValidator.validate_cost_data(df)
        assert is_valid is False
    
    def test_negative_costs(self):
        """Test validation with negative costs."""
        df = pd.DataFrame({
            'timestamp': [datetime.now()],
            'service': ['ec2'],
            'region': ['us-east-1'],
            'cost': [-100.0]
        })
        
        is_valid, message = DataValidator.validate_cost_data(df)
        assert is_valid is False

    def test_aws_billing_column_mapping(self):
        df = pd.DataFrame({
            'line_item_usage_start_date': [datetime(2024, 1, 1, 0, 0)],
            'product_servicename': ['ec2'],
            'product_region': ['us-east-1'],
            'line_item_unblended_cost': [100.0],
            'line_item_usage_amount': [5.0]
        })

        mapped = map_aws_billing_columns(df)

        assert 'timestamp' in mapped.columns
        assert 'service' in mapped.columns
        assert 'region' in mapped.columns
        assert 'total_cost' in mapped.columns
        assert 'usage_quantity' in mapped.columns
        assert mapped['timestamp'].dtype == object or 'datetime' in str(mapped['timestamp'].dtype)

    def test_aws_billing_interval_and_cost_fallback(self):
        df = pd.DataFrame({
            'identity_time_interval': ['2024-01-01T00:00:00Z/2024-01-01T01:00:00Z'],
            'product_servicecode': ['AmazonEC2'],
            'product_region_code': ['us-east-1'],
            'line_item_blended_cost': [150.0],
            'line_item_usage_amount': [3.0]
        })

        mapped = map_aws_billing_columns(df)

        assert 'timestamp' in mapped.columns
        assert 'service' in mapped.columns
        assert 'region' in mapped.columns
        assert 'total_cost' in mapped.columns
        assert 'usage_quantity' in mapped.columns
        assert pd.to_datetime(mapped['timestamp']).notna().all()
        assert mapped['total_cost'].iloc[0] == 150.0


class TestIsolationForest:
    """Test Isolation Forest anomaly detection."""
    
    @pytest.fixture
    def model(self):
        """Create model instance."""
        return IsolationForestModel(contamination=0.1)
    
    def test_training(self, model):
        """Test model training."""
        X = np.random.randn(100, 3)
        model.train(X)
        
        assert model.is_fitted is True
    
    def test_prediction(self, model):
        """Test predictions."""
        X_train = np.random.randn(100, 3)
        model.train(X_train)
        
        X_test = np.random.randn(10, 3)
        flags, scores = model.predict(X_test)
        
        assert len(flags) == 10
        assert len(scores) == 10
        assert all(f in [0, 1] for f in flags)


class TestProphetForecasting:
    """Test Prophet forecasting model."""
    
    @pytest.fixture
    def model(self):
        """Create model instance."""
        return ProphetForecastingModel()
    
    @pytest.fixture
    def timeseries_data(self):
        """Create time series data."""
        dates = pd.date_range('2024-01-01', periods=365)
        values = np.cumsum(np.random.randn(365))
        
        return pd.DataFrame({
            'ds': dates,
            'y': values
        })
    
    def test_training(self, model, timeseries_data):
        """Test model training."""
        model.train(timeseries_data)
        
        assert 'total' in model.models
    
    def test_forecasting(self, model, timeseries_data):
        """Test forecasting."""
        model.train(timeseries_data)
        forecast = model.forecast(periods=30)
        
        assert len(forecast) == 30
        assert 'yhat' in forecast.columns


class TestRandomForest:
    """Test Random Forest optimization."""
    
    @pytest.fixture
    def model(self):
        """Create model instance."""
        return RandomForestOptimizer()
    
    def test_training(self, model):
        """Test model training."""
        X = np.random.randn(100, 4)
        y = np.random.randn(100)
        
        model.train(X, y)
        
        assert model.is_fitted is True
    
    def test_predictions(self, model):
        """Test predictions."""
        X_train = np.random.randn(100, 4)
        y_train = np.random.randn(100)
        model.train(X_train, y_train)
        
        X_test = np.random.randn(10, 4)
        predictions = model.predict(X_test)
        
        assert len(predictions) == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
