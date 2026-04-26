"""
Cost optimization service using Random Forest.
"""

import pandas as pd
import numpy as np
import logging
from app.ml.random_forest import RandomForestOptimizer

logger = logging.getLogger(__name__)


class OptimizationService:
    """Service for cost optimization recommendations."""
    
    def __init__(self):
        """Initialize optimization service."""
        self.model = RandomForestOptimizer()
        self.is_trained = False
    
    def prepare_optimization_data(self, df: pd.DataFrame) -> tuple:
        """
        Prepare features for cost optimization model.
        
        Args:
            df: Input dataframe
            
        Returns:
            Tuple of (features, target, feature_names)
        """
        # Feature engineering
        features_df = df.copy()
        
        # Create numerical features
        features_list = []
        feature_names = []
        
        # Cost features
        if 'total_cost' in features_df.columns:
            features_list.append(features_df['total_cost'].values)
            feature_names.append('total_cost')
        
        if 'cost_velocity' in features_df.columns:
            features_list.append(features_df['cost_velocity'].fillna(0).values)
            feature_names.append('cost_velocity')
        
        if 'rolling_avg_7d' in features_df.columns:
            features_list.append(features_df['rolling_avg_7d'].fillna(0).values)
            feature_names.append('rolling_avg_7d')
        
        if 'rolling_avg_30d' in features_df.columns:
            features_list.append(features_df['rolling_avg_30d'].fillna(0).values)
            feature_names.append('rolling_avg_30d')
        
        # Service encoding
        if 'service' in features_df.columns:
            service_encoded = pd.factorize(features_df['service'])[0]
            features_list.append(service_encoded)
            feature_names.append('service_encoded')
        
        # Region encoding
        if 'region' in features_df.columns:
            region_encoded = pd.factorize(features_df['region'])[0]
            features_list.append(region_encoded)
            feature_names.append('region_encoded')
        
        X = np.column_stack(features_list)
        
        # Target: potential savings (inverse relationship with cost)
        y = features_df['total_cost'].values
        
        return X, y, feature_names
    
    def train(self, df: pd.DataFrame) -> None:
        """
        Train optimization model.
        
        Args:
            df: Training dataframe
        """
        try:
            logger.info("Training optimization model")
            X, y, feature_names = self.prepare_optimization_data(df)
            self.model.train(X, y, feature_names)
            self.is_trained = True
            logger.info("Optimization model trained")
        except Exception as e:
            logger.error(f"Error training optimization model: {e}")
            raise
    
    def get_recommendations(self, df: pd.DataFrame, top_n: int = 10) -> list:
        """
        Get cost optimization recommendations.
        
        Args:
            df: Input dataframe
            top_n: Number of recommendations
            
        Returns:
            List of recommendation dictionaries
        """
        if not self.is_trained:
            logger.warning("Model not trained, training on input data")
            self.train(df)
        
        try:
            recommendations = []
            
            # Group by service and region
            for (service, region), group in df.groupby(['service', 'region']):
                avg_cost = group['total_cost'].mean()
                max_cost = group['total_cost'].max()
                min_cost = group['total_cost'].min()
                std_cost = group['total_cost'].std()
                
                # Identify patterns for recommendations
                if std_cost > avg_cost * 0.3:  # High variability
                    recommendation = {
                        'service': service,
                        'region': region,
                        'recommendation_type': 'cost_stability',
                        'suggestion': f"Stabilize {service} usage in {region} to reduce cost fluctuations",
                        'estimated_savings': std_cost,
                        'confidence_score': min(0.95, (std_cost / max_cost)),
                        'priority': 1
                    }
                    recommendations.append(recommendation)
                
                # Right-sizing recommendation
                if max_cost > avg_cost * 1.5:
                    recommendation = {
                        'service': service,
                        'region': region,
                        'recommendation_type': 'right_sizing',
                        'suggestion': f"Right-size {service} instances in {region}",
                        'estimated_savings': (max_cost - avg_cost) * 0.3,
                        'confidence_score': 0.85,
                        'priority': 2
                    }
                    recommendations.append(recommendation)
                
                # Reserved instances recommendation
                if avg_cost > 100:  # Significant cost
                    recommendation = {
                        'service': service,
                        'region': region,
                        'recommendation_type': 'reserved_capacity',
                        'suggestion': f"Consider reserved capacity for {service} in {region}",
                        'estimated_savings': avg_cost * 0.2,
                        'confidence_score': 0.8,
                        'priority': 3
                    }
                    recommendations.append(recommendation)
            
            # Sort by estimated savings
            recommendations.sort(key=lambda x: x['estimated_savings'], reverse=True)
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations[:top_n]
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise
    
    def get_feature_importance(self) -> Dict:
        """
        Get feature importance for cost optimization.
        
        Returns:
            Feature importance dictionary
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        return self.model.get_feature_importance()
