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
from app.ml.prophet_model import ProphetForecastingModel
from app.ml.random_forest import RandomForestOptimizer


class TestDataPreprocessor:
    """Test data preprocessing."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='h'),
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


class TestAnomalyDetectionService:
    """Test AnomalyDetectionService."""

    @pytest.fixture
    def sample_billing_data(self):
        dates = pd.date_range("2024-01-01", periods=200, freq="h")
        np.random.seed(42)
        return pd.DataFrame({
            "timestamp": dates,
            "account_id": ["acc-001"] * 200,
            "service": np.random.choice(["ec2", "s3", "rds"], 200),
            "usage_type": np.random.choice(["BoxUsage", "Storage"], 200),
            "region": np.random.choice(["us-east-1", "us-west-2"], 200),
            "environment": np.random.choice(["prod", "dev"], 200),
            "instance_type": np.random.choice(["t3.micro", "m5.large"], 200),
            "cost": np.random.uniform(5, 500, 200),
            "usage_amount": np.random.uniform(100, 10000, 200),
        })

    def test_train_and_detect(self, sample_billing_data):
        from app.services.anomaly_detection import AnomalyDetectionService
        svc = AnomalyDetectionService(contamination=0.05)
        result = svc.detect_anomalies(sample_billing_data)
        assert "anomaly_flag" in result.columns
        assert "anomaly_score" in result.columns
        assert "explanation" in result.columns
        assert result["anomaly_flag"].isin([0, 1]).all()
        assert result["anomaly_score"].between(0, 1).all()

    def test_get_top_anomalies(self, sample_billing_data):
        from app.services.anomaly_detection import AnomalyDetectionService
        svc = AnomalyDetectionService(contamination=0.05)
        result = svc.detect_anomalies(sample_billing_data)
        top = svc.get_top_anomalies(result, top_n=3)
        assert len(top) <= 3
        assert (top["anomaly_flag"] == 1).all()

    def test_save_and_load_artifacts(self, sample_billing_data, tmp_path):
        from app.services.anomaly_detection import AnomalyDetectionService
        svc = AnomalyDetectionService(contamination=0.05)
        svc.train(sample_billing_data)
        svc.save_artifacts(str(tmp_path))
        loaded = AnomalyDetectionService.load_artifacts(str(tmp_path))
        assert loaded.is_trained
        result = loaded.detect_anomalies(sample_billing_data)
        assert "anomaly_flag" in result.columns


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
        
        assert 'default' in model.models
    
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


class TestExplanationColumns:
    """Test that the explanation columns exist in the anomalies table."""

    def test_columns_exist(self):
        from sqlalchemy import inspect
        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            inspector = inspect(db.connection())
            columns = {c["name"]: c for c in inspector.get_columns("anomalies")}
            for col in (
                "explanation",
                "cost_zscore",
                "cost_ratio_p95",
                "daily_spend_zscore",
                "cost_per_unit_ratio",
                "error_count",
            ):
                assert col in columns, f"Missing column: {col}"
        finally:
            db.close()

    def test_migration_upgrade_and_downgrade(self):
        from alembic.config import Config
        from alembic import command
        from sqlalchemy import inspect, text as sql_text
        from app.core.database import engine
        from pathlib import Path

        alembic_cfg = Config()
        # alembic dir is at backend/alembic (1 level up from tests/)
        alembic_dir = str(Path(__file__).resolve().parent.parent / "alembic")
        alembic_cfg.set_main_option("script_location", alembic_dir)
        from app.core.settings import get_settings
        _settings = get_settings()
        alembic_cfg.set_main_option("sqlalchemy.url", _settings.database_url)

        # Downgrade to base
        command.downgrade(alembic_cfg, "base")
        with engine.connect() as conn:
            if engine.dialect.name == "postgresql":
                result = conn.execute(
                    sql_text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = 'anomalies' AND column_name = 'cost_zscore'"
                    )
                )
                assert result.first() is None
            else:
                inspector = inspect(engine)
                columns = {c["name"] for c in inspector.get_columns("anomalies")}
                assert "cost_zscore" not in columns

        # Upgrade again
        command.upgrade(alembic_cfg, "head")
        with engine.connect() as conn:
            if engine.dialect.name == "postgresql":
                result = conn.execute(
                    sql_text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = 'anomalies' AND column_name = 'cost_zscore'"
                    )
                )
                assert result.first() is not None
            else:
                inspector = inspect(engine)
                columns = {c["name"] for c in inspector.get_columns("anomalies")}
                assert "cost_zscore" in columns


class TestScoreAnomalies:
    """Test the batch anomaly scoring job."""

    @pytest.fixture
    def sample_billing_data(self):
        np.random.seed(99)
        return pd.DataFrame({
            "timestamp": pd.date_range("2024-06-01", periods=150, freq="h"),
            "account_id": ["acc-test"] * 150,
            "service": np.random.choice(["ec2", "s3"], 150),
            "usage_type": np.random.choice(["BoxUsage", "Storage"], 150),
            "region": np.random.choice(["us-east-1"], 150),
            "environment": np.random.choice(["prod"], 150),
            "instance_type": np.random.choice(["t3.micro"], 150),
            "cost": np.random.uniform(10, 500, 150),
            "usage_amount": np.random.uniform(100, 5000, 150),
        })

    def test_score_and_persist(self, sample_billing_data):
        from app.services.score_anomalies import score_and_persist
        from app.core.database import SessionLocal
        from app.models import db_models

        inserted = score_and_persist(
            sample_billing_data,
            contamination=0.1,
            batch_label="test_batch",
        )
        assert isinstance(inserted, int)
        assert inserted >= 0

        # Verify newly inserted rows have explanation as a proper dict
        db = SessionLocal()
        try:
            rows = (
                db.query(db_models.Anomaly)
                .filter(db_models.Anomaly.anomaly_flag == True)
                .order_by(db_models.Anomaly.id.desc())
                .limit(inserted if inserted > 0 else 1)
                .all()
            )
            for row in rows:
                if row.explanation is not None:
                    # Stored as TEXT, we verify it's valid JSON
                    import json as _json
                    parsed = _json.loads(row.explanation) if isinstance(row.explanation, str) else row.explanation
                    assert isinstance(parsed, dict), (
                        f"Expected dict, got {type(row.explanation)}: {row.explanation!r}"
                    )
                    # Verify the expected keys exist
                    assert "human_readable" in parsed or "cost_zscore" in parsed
        finally:
            db.close()


class TestNotifications:
    """Test notification builder functions."""

    def test_build_pagerduty_payload(self):
        from app.services.notifications import build_pagerduty_payload

        anomaly = {
            "id": 42,
            "account_id": "acct-001",
            "service": "EC2",
            "region": "us-east-1",
            "usage_type": "BoxUsage",
            "cost_value": 4210.00,
            "anomaly_score": 0.94,
            "explanation": {
                "cost_zscore": 8.3,
                "cost_ratio_p95": 12.1,
                "cost_ratio_mean": 9.4,
                "daily_spend_zscore": 1.2,
                "cost_per_unit_ratio": 0.9,
                "error_count": 0,
                "human_readable": "Cost is 8.3x SDs above baseline",
            },
        }

        payload = build_pagerduty_payload(anomaly)

        assert payload["event_action"] == "trigger"
        assert payload["dedup_key"] == "fincloud-anomaly-42"
        assert payload["payload"]["severity"] == "critical"
        assert "Cost is 8.3x SDs" in payload["payload"]["custom_details"]["explanation_summary"]
        assert payload["payload"]["custom_details"]["explanation"] == anomaly["explanation"]

    def test_build_pagerduty_payload_no_explanation(self):
        from app.services.notifications import build_pagerduty_payload

        anomaly = {
            "id": 43,
            "cost_value": 100.0,
            "anomaly_score": 0.5,
        }

        payload = build_pagerduty_payload(anomaly)
        assert payload["payload"]["severity"] == "info"
        assert payload["payload"]["custom_details"].get("explanation_summary") is not None
        assert "explanation" not in payload["payload"]["custom_details"] or payload["payload"]["custom_details"]["explanation"] == {}

    def test_build_slack_message(self):
        from app.services.notifications import build_slack_message

        anomaly = {
            "id": 44,
            "account_id": "acct-002",
            "service": "RDS",
            "region": "us-west-2",
            "cost_value": 812.00,
            "anomaly_score": 0.72,
            "explanation": {
                "cost_zscore": 1.8,
                "cost_ratio_p95": 1.2,
                "cost_ratio_mean": 1.1,
                "daily_spend_zscore": 0.4,
                "cost_per_unit_ratio": 7.2,
                "error_count": 0,
                "human_readable": "Cost-per-unit is 7.2x baseline",
            },
        }

        msg = build_slack_message(anomaly)

        assert msg["text"] is not None
        assert "blocks" in msg
        assert any("Cost-per-unit is 7.2x" in str(b) for b in msg["blocks"])
        assert any("RDS" in str(b) for b in msg["blocks"])


class TestAnomalyAPI:
    """Test the anomaly API endpoints with filter params."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.api.dependencies import require_authenticated_user

        # Override auth dependency to bypass authentication
        async def _mock_user():
            return None

        app.dependency_overrides[require_authenticated_user] = _mock_user
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()

    def test_get_anomalies_no_auth_required(self, client):
        """With auth bypass, the endpoint should return data."""
        resp = client.get("/api/v1/anomalies?days=7")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert "anomalies" in body["data"]

    def test_get_anomalies_filter_params_accepted(self, client):
        """Filter query params should not cause errors."""
        resp = client.get(
            "/api/v1/anomalies?days=30&cost_zscore_gt=3&min_score=0",
        )
        assert resp.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
