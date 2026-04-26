"""
Random Forest model for cost optimization recommendations.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class RandomForestOptimizer:
    """Random Forest model for cost optimization recommendations."""
    
    def __init__(self, n_estimators: int = 100, random_state: int = 42, max_depth: int = 15):
        """
        Initialize Random Forest model.
        
        Args:
            n_estimators: Number of trees
            random_state: Random seed
            max_depth: Maximum tree depth
        """
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.max_depth = max_depth
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            max_depth=max_depth,
            n_jobs=-1
        )
        self.is_fitted = False
        self.feature_names = None
        
    def train(self, X: np.ndarray, y: np.ndarray, feature_names: List[str] = None) -> None:
        """
        Train Random Forest model.
        
        Args:
            X: Feature array (n_samples, n_features)
            y: Target array (n_samples,)
            feature_names: Names of features
        """
        try:
            logger.info(f"Training Random Forest with {len(X)} samples, {X.shape[1]} features")
            self.model.fit(X, y)
            self.is_fitted = True
            self.feature_names = feature_names
            logger.info("Random Forest training completed")
        except Exception as e:
            logger.error(f"Error training Random Forest: {e}")
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict cost savings potential.
        
        Args:
            X: Feature array
            
        Returns:
            Prediction array
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained first")
        
        return self.model.predict(X)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained first")
        
        importances = self.model.feature_importances_
        
        if self.feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(importances))]
        else:
            feature_names = self.feature_names
        
        return dict(zip(feature_names, importances.tolist()))
    
    def get_top_features(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Get top N important features.
        
        Args:
            top_n: Number of top features
            
        Returns:
            List of (feature_name, importance_score) tuples
        """
        importances = self.get_feature_importance()
        sorted_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)
        return sorted_features[:top_n]
    
    def identify_optimization_opportunities(self, df: pd.DataFrame, 
                                           cost_column: str = 'cost',
                                           threshold: float = 0.7) -> List[Dict]:
        """
        Identify cost optimization opportunities.
        
        Args:
            df: Input dataframe with features
            cost_column: Name of cost column
            threshold: Savings potential threshold (0-1)
            
        Returns:
            List of optimization recommendations
        """
        try:
            recommendations = []
            
            # Get feature importance
            importances = self.get_feature_importance()
            top_features = self.get_top_features(top_n=3)
            
            # Analyze by service and region
            for service in df.get('service', ['Unknown']):
                service_df = df[df['service'] == service] if 'service' in df.columns else df
                
                avg_cost = service_df[cost_column].mean()
                max_cost = service_df[cost_column].max()
                cost_range = max_cost - avg_cost
                
                # Calculate potential savings
                savings_potential = (cost_range / max_cost) if max_cost > 0 else 0
                
                if savings_potential > threshold:
                    recommendation = {
                        'service': service,
                        'recommendation_type': 'cost_consolidation',
                        'suggestion': f"Consolidate {service} resources to reduce costs",
                        'estimated_savings': savings_potential * avg_cost,
                        'confidence_score': min(0.95, savings_potential + 0.1),
                        'priority': 1 if savings_potential > 0.5 else 2
                    }
                    recommendations.append(recommendation)
            
            return recommendations
        except Exception as e:
            logger.error(f"Error identifying optimization opportunities: {e}")
            return []
