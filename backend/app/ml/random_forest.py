"""
Random Forest + XGBoost ensemble model for FinOps cost optimization.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    n_samples: int
    n_features: int
    feature_names: List[str]
    feature_importances: Dict[str, float]
    oob_score: Optional[float] = None
    xgb_score: Optional[float] = None
    anomaly_contamination: float = 0.05
    extra: Dict = field(default_factory=dict)


@dataclass
class ResourceScore:
    resource_id: str
    service: str
    region: str
    savings_potential: float
    anomaly_score: float
    is_anomaly: bool
    feature_vector: Optional[np.ndarray] = None
    rec_type: str = "optimization"
    confidence: float = 0.5


class RandomForestOptimizer:
    DOWNSIZE_MAP: Dict[str, str] = {
        "t3.2xlarge": "t3.xlarge",
        "t3.xlarge":  "t3.large",
        "t3.large":   "t3.medium",
        "t3.medium":  "t3.micro",
        "m5.4xlarge": "m5.2xlarge",
        "m5.2xlarge": "m5.xlarge",
        "m5.xlarge":  "m5.large",
        "m5.large":   "t3.large",
        "r5.4xlarge": "r5.2xlarge",
        "r5.2xlarge": "r5.xlarge",
        "r5.xlarge":  "r5.large",
        "c5.4xlarge": "c5.2xlarge",
        "c5.2xlarge": "c5.xlarge",
        "c5.xlarge":  "c5.large",
    }

    SPOT_ELIGIBLE = {"ec2", "ecs", "lambda", "eks", "batch", "emr"}

    def __init__(
        self,
        n_estimators: int = 150,
        random_state: int = 42,
        max_depth: int = 15,
        anomaly_contamination: float = 0.05,
    ) -> None:
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.max_depth = max_depth
        self.anomaly_contamination = anomaly_contamination

        self._regressor = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            oob_score=True,
            n_jobs=-1,
            min_samples_leaf=3,
            min_samples_split=5,
            max_features='sqrt',
        )
        self._xgb = XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            reg_alpha=0.1,
        )
        self._classifier = LogisticRegression(
            random_state=random_state,
            max_iter=500,
            multi_class='multinomial',
        )
        self._calibrator = IsotonicRegression(out_of_bounds='clip')
        self._calibrator_fitted = False

        self._isolation = IsolationForest(
            n_estimators=100,
            contamination=anomaly_contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self._scaler = StandardScaler()
        self._label_encoders: Dict[str, Dict] = {}
        self.is_fitted: bool = False
        self.metrics: Optional[ModelMetrics] = None
        self._rec_type_encoder: Dict[str, int] = {}

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str],
        rec_types: Optional[np.ndarray] = None,
    ) -> RandomForestOptimizer:
        if X.shape[0] < 10:
            raise ValueError(
                f"Need at least 10 samples to fit; got {X.shape[0]}."
            )

        logger.info(
            "Fitting RandomForestOptimizer: %d samples, %d features",
            X.shape[0], X.shape[1],
        )

        X_scaled = self._scaler.fit_transform(X)

        self._regressor.fit(X_scaled, y)
        self._xgb.fit(X_scaled, y)

        self._isolation.fit(X_scaled)

        if rec_types is not None and len(np.unique(rec_types)) > 1:
            unique_types = sorted(np.unique(rec_types))
            self._rec_type_encoder = {t: i for i, t in enumerate(unique_types)}
            y_cls = np.array([self._rec_type_encoder[t] for t in rec_types])
            self._classifier.fit(X_scaled, y_cls)

        rf_pred = self._regressor.predict(X_scaled)
        self._calibrator.fit(y, rf_pred)
        self._calibrator_fitted = True

        self.is_fitted = True
        oob = getattr(self._regressor, "oob_score_", None)
        logger.info("Regressor OOB R²: %s", f"{oob:.4f}" if oob else "n/a")

        importances = dict(
            zip(feature_names, self._regressor.feature_importances_.tolist())
        )
        self.metrics = ModelMetrics(
            n_samples=X.shape[0],
            n_features=X.shape[1],
            feature_names=feature_names,
            feature_importances=importances,
            oob_score=oob,
            anomaly_contamination=self.anomaly_contamination,
            extra={'rec_type_classes': list(self._rec_type_encoder.keys())},
        )
        return self

    def predict_savings(self, X: np.ndarray) -> np.ndarray:
        self._assert_fitted()
        X_scaled = self._scaler.transform(X)
        rf_pred = self._regressor.predict(X_scaled)
        xgb_pred = self._xgb.predict(X_scaled)
        ensemble = 0.6 * rf_pred + 0.4 * xgb_pred
        return np.clip(ensemble, 0, None)

    def predict_anomaly(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        self._assert_fitted()
        X_scaled = self._scaler.transform(X)
        labels = self._isolation.predict(X_scaled)
        scores = self._isolation.decision_function(X_scaled)
        return labels, scores

    def predict_rec_type(self, X: np.ndarray, services: List[str]) -> np.ndarray:
        if not self._rec_type_encoder:
            return np.array(['right_sizing'] * X.shape[0])

        X_scaled = self._scaler.transform(X)
        type_ids = self._classifier.predict(X_scaled)
        inv_map = {v: k for k, v in self._rec_type_encoder.items()}
        return np.array([inv_map[tid] for tid in type_ids])

    def predict_confidence(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        if not self._calibrator_fitted:
            return np.clip(1.0 - np.abs(y_true - y_pred) / (np.abs(y_true) + 1e-6), 0, 1)
        calibrated = self._calibrator.predict(y_pred)
        return np.clip(calibrated, 0, 1)

    def score_resources(
        self,
        X: np.ndarray,
        resource_ids: List[str],
        services: List[str],
        regions: List[str],
    ) -> List[ResourceScore]:
        self._assert_fitted()
        savings = self.predict_savings(X)
        anomaly_labels, anomaly_scores = self.predict_anomaly(X)
        rec_types = self.predict_rec_type(X, services)

        results: List[ResourceScore] = []
        for i in range(len(resource_ids)):
            results.append(ResourceScore(
                resource_id=resource_ids[i],
                service=services[i],
                region=regions[i],
                savings_potential=float(savings[i]),
                anomaly_score=float(anomaly_scores[i]),
                is_anomaly=bool(anomaly_labels[i] == -1),
                feature_vector=X[i],
                rec_type=str(rec_types[i]),
                confidence=0.0,
            ))
        return results

    def get_feature_importance(self) -> Dict[str, float]:
        self._assert_fitted()
        return dict(
            sorted(
                self.metrics.feature_importances.items(),
                key=lambda kv: kv[1],
                reverse=True,
            )
        )

    def get_top_features(self, top_n: int = 5) -> List[Tuple[str, float]]:
        return list(self.get_feature_importance().items())[:top_n]

    def _assert_fitted(self) -> None:
        if not self.is_fitted:
            raise RuntimeError(
                "Model has not been trained yet. Call fit() first."
            )

    @staticmethod
    def suggest_downsize(instance_type: str) -> Optional[str]:
        return RandomForestOptimizer.DOWNSIZE_MAP.get(instance_type)
