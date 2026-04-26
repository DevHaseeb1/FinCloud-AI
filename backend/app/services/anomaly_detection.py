"""
Anomaly detection service using Isolation Forest.
"""

import pandas as pd
import numpy as np
import logging
from app.ml.isolation_forest import IsolationForestModel

logger = logging.getLogger(__name__)


class AnomalyDetectionService:
    """Service for detecting cost anomalies."""
    
    def __init__(self, contamination: float = 0.05):
        """
        Initialize anomaly detection service.
        
        Args:
            contamination: Expected anomaly proportion
        """
        self.model = IsolationForestModel(contamination=contamination)
        self.is_trained = False
    
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for anomaly detection.
        
        Args:
            df: Input dataframe
            
        Returns:
            Feature array
        """
        feature_cols = []
        
        # Use cost-related features
        if 'total_cost' in df.columns:
            feature_cols.append('total_cost')
        if 'cost_velocity' in df.columns:
            feature_cols.append('cost_velocity')
        if 'rolling_avg_7d' in df.columns:
            feature_cols.append('rolling_avg_7d')
        if 'rolling_avg_30d' in df.columns:
            feature_cols.append('rolling_avg_30d')
        
        # Handle missing features
        if not feature_cols:
            # Fallback to just cost
            if 'total_cost' in df.columns:
                return df[['total_cost']].values
            else:
                raise ValueError("No suitable features for anomaly detection")
        
        # Fill NaN values
        features = df[feature_cols].fillna(0).values
        
        # Normalize features
        features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)
        
        return features
    
    def train(self, df: pd.DataFrame) -> None:
        """
        Train anomaly detection model.
        
        Args:
            df: Training dataframe
        """
        try:
            logger.info("Training anomaly detection model")
            features = self.prepare_features(df)
            self.model.train(features)
            self.is_trained = True
            logger.info("Anomaly detection model trained")
        except Exception as e:
            logger.error(f"Error training anomaly detection model: {e}")
            raise
    
    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect anomalies in cost data.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dataframe with anomaly columns
        """
        if not self.is_trained:
            logger.warning("Model not trained, training on input data")
            self.train(df)
        
        try:
            features = self.prepare_features(df)
            anomaly_flags, anomaly_scores = self.model.predict(features)
            
            result = df.copy()
            result['anomaly_flag'] = anomaly_flags
            result['anomaly_score'] = anomaly_scores
            
            # Determine explanation
            result['explanation'] = result.apply(
                lambda row: self._get_explanation(row),
                axis=1
            )
            
            num_anomalies = anomaly_flags.sum()
            logger.info(f"Detected {num_anomalies} anomalies out of {len(df)} records")
            
            return result
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            raise
    
    @staticmethod
    def _get_explanation(row) -> str:
        """
        Generate explanation for anomaly.
        
        Args:
            row: Data row
            
        Returns:
            Explanation string
        """
        if row.get('anomaly_flag', 0) == 0:
            return "Normal cost pattern"
        
        score = row.get('anomaly_score', 0)
        service = row.get('service', 'Unknown')
        
        if score > 0.8:
            return f"Severe anomaly detected in {service} costs"
        elif score > 0.6:
            return f"Significant cost spike in {service}"
        else:
            return f"Minor anomaly in {service}"
    
    def get_top_anomalies(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        Get top N anomalies by score.
        
        Args:
            df: Dataframe with anomaly scores
            top_n: Number of top anomalies
            
        Returns:
            Top anomalies
        """
        return df[df['anomaly_flag'] == 1].nlargest(top_n, 'anomaly_score')
