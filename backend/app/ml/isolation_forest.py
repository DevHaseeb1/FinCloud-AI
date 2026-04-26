"""
Isolation Forest model for anomaly detection.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class IsolationForestModel:
    """Isolation Forest anomaly detection model."""
    
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        """
        Initialize Isolation Forest model.
        
        Args:
            contamination: Expected proportion of anomalies
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.is_fitted = False
        
    def train(self, features: np.ndarray) -> None:
        """
        Train the Isolation Forest model.
        
        Args:
            features: Training feature array (n_samples, n_features)
        """
        try:
            logger.info(f"Training Isolation Forest with {len(features)} samples")
            self.model.fit(features)
            self.is_fitted = True
            logger.info("Isolation Forest training completed")
        except Exception as e:
            logger.error(f"Error training Isolation Forest: {e}")
            raise
    
    def predict(self, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies on new data.
        
        Args:
            features: Feature array (n_samples, n_features)
            
        Returns:
            Tuple of (anomaly_flags, anomaly_scores)
            - anomaly_flags: -1 for anomaly, 1 for normal
            - anomaly_scores: Negative values indicate anomalies
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained first")
        
        try:
            predictions = self.model.predict(features)
            scores = self.model.score_samples(features)
            
            # Convert predictions: -1 (anomaly) -> 1, 1 (normal) -> 0
            anomaly_flags = (predictions == -1).astype(int)
            
            # Normalize scores to [0, 1] range
            normalized_scores = 1 / (1 + np.exp(scores))
            
            return anomaly_flags, normalized_scores
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            raise
    
    def get_anomaly_score(self, features: np.ndarray) -> np.ndarray:
        """
        Get anomaly scores (0-1, higher is more anomalous).
        
        Args:
            features: Feature array
            
        Returns:
            Anomaly scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained first")
        
        scores = self.model.score_samples(features)
        # Normalize to [0, 1]
        normalized_scores = 1 / (1 + np.exp(scores))
        return normalized_scores
    
    def detect_anomalies(self, df: pd.DataFrame, feature_columns: list) -> pd.DataFrame:
        """
        Detect anomalies in a dataframe.
        
        Args:
            df: Input dataframe
            feature_columns: Column names to use as features
            
        Returns:
            DataFrame with anomaly_flag and anomaly_score columns
        """
        try:
            features = df[feature_columns].values
            anomaly_flags, anomaly_scores = self.predict(features)
            
            result_df = df.copy()
            result_df['anomaly_flag'] = anomaly_flags
            result_df['anomaly_score'] = anomaly_scores
            
            return result_df
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            raise
