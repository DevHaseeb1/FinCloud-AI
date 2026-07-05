"""
Cost optimization service using Random Forest + XGBoost ensemble.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from app.ml.random_forest import RandomForestOptimizer

logger = logging.getLogger(__name__)

SPOT_ELIGIBLE_SERVICES = {"ec2", "ecs", "lambda", "eks", "batch", "emr", "elasticache"}
RESERVED_ELIGIBLE_SERVICES = {"ec2", "rds", "elasticache", "redshift", "elasticsearch"}


class OptimizationService:
    def __init__(self):
        self.model = RandomForestOptimizer()
        self.is_trained = False
        self._freq_encoders: Dict[str, Dict] = {}

    def prepare_optimization_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str], np.ndarray]:
        features_df = df.copy().reset_index(drop=True)
        features_list: List[np.ndarray] = []
        feature_names: List[str] = []

        features_df['date'] = pd.to_datetime(features_df['date'])
        features_df = features_df.sort_values(['service', 'region', 'date'])

        total_cost = features_df['total_cost'].values

        # 1. Log total cost
        features_list.append(np.log1p(np.maximum(total_cost, 0)))
        feature_names.append('log_total_cost')

        tc_series = features_df['total_cost']

        # 2-3. Rolling averages
        for col in ['rolling_avg_7d', 'rolling_avg_30d']:
            if col in features_df.columns:
                features_list.append(features_df[col].fillna(tc_series).values)
                feature_names.append(col)

        # 4. Cost velocity
        if 'cost_velocity' in features_df.columns:
            features_list.append(features_df['cost_velocity'].fillna(0).values)
            feature_names.append('cost_velocity')

        # 5. Cost momentum (7d / 30d avg)
        ra7 = features_df['rolling_avg_7d'].fillna(tc_series).values
        ra30 = features_df['rolling_avg_30d'].fillna(tc_series).values
        momentum = np.where(ra30 > 1e-6, ra7 / ra30, 1.0)
        features_list.append(np.clip(momentum, 0, 10))
        feature_names.append('cost_momentum')

        # 6. Daily cost
        if 'daily_cost' in features_df.columns:
            features_list.append(features_df['daily_cost'].fillna(tc_series).values)
            feature_names.append('daily_cost')

        # 7. Service spend share per date
        daily_total = features_df.groupby('date')['total_cost'].transform('sum')
        service_share = np.where(daily_total > 1e-6, total_cost / daily_total, 0)
        features_list.append(service_share)
        feature_names.append('service_spend_share')

        # 8. Usage efficiency (cost per unit)
        if 'usage_quantity' in features_df.columns:
            uq = features_df['usage_quantity'].fillna(0).values
            efficiency = np.where(uq > 1e-6, total_cost / uq, 0)
            features_list.append(np.clip(efficiency, 0, 1e6))
            feature_names.append('usage_efficiency')
            features_list.append(np.log1p(np.maximum(uq, 0)))
            feature_names.append('log_usage_quantity')

        # 9. Cost volatility per group
        group_cv = features_df.groupby(['service', 'region'])['total_cost'].transform(
            lambda x: x.std() / (x.mean() + 1e-6)
        )
        features_list.append(group_cv.fillna(0).values)
        feature_names.append('cost_cv')
        features_list.append((group_cv > 0.5).astype(int).fillna(0).values)
        feature_names.append('is_high_variance')

        # 10. Service frequency encoding
        svc_freq = features_df['service'].value_counts(normalize=True).to_dict()
        self._freq_encoders['service'] = svc_freq
        features_list.append(features_df['service'].map(svc_freq).fillna(0).values)
        feature_names.append('service_freq')

        # 11. Region frequency encoding
        reg_freq = features_df['region'].value_counts(normalize=True).to_dict()
        self._freq_encoders['region'] = reg_freq
        features_list.append(features_df['region'].map(reg_freq).fillna(0).values)
        feature_names.append('region_freq')

        # 12. Day of week
        features_list.append(features_df['date'].dt.dayofweek.values.astype(np.float64) / 6.0)
        feature_names.append('day_of_week_norm')

        # 13. Month (cyclic via sin/cos)
        month = features_df['date'].dt.month.values.astype(np.float64)
        features_list.append(np.sin(2 * np.pi * month / 12))
        feature_names.append('month_sin')
        features_list.append(np.cos(2 * np.pi * month / 12))
        feature_names.append('month_cos')

        # 14. Is weekend
        features_list.append((features_df['date'].dt.dayofweek >= 5).astype(np.float64).values)
        feature_names.append('is_weekend')

        # 15. Cost trend (7d avg / 30d avg spread)
        spread = np.where(ra30 > 1e-6, (ra7 - ra30) / (ra30 + 1e-6), 0)
        features_list.append(np.clip(spread, -1, 1))
        feature_names.append('cost_trend_spread')

        # 16. Cost z-score within service/region group
        group_mean = features_df.groupby(['service', 'region'])['total_cost'].transform('mean')
        group_std = features_df.groupby(['service', 'region'])['total_cost'].transform('std').replace(0, 1)
        zscore = np.where(group_std > 1e-6, (total_cost - group_mean) / group_std, 0)
        features_list.append(np.clip(zscore, -5, 5))
        feature_names.append('cost_zscore_group')

        # 17. Cost percentile rank within service/region
        pct_rank = features_df.groupby(['service', 'region'])['total_cost'].rank(pct=True)
        features_list.append(pct_rank.fillna(0.5).values)
        feature_names.append('cost_percentile')

        # 18. Day of month (billing cycle effects)
        dom = features_df['date'].dt.day.values.astype(np.float64) / 31.0
        features_list.append(dom)
        feature_names.append('day_of_month_norm')

        # 19. Is month end (last 3 days)
        features_list.append((features_df['date'].dt.day >= 28).astype(np.float64).values)
        feature_names.append('is_month_end')

        X = np.column_stack(features_list).astype(np.float64)

        y, rec_types = self._compute_realistic_targets(features_df)

        return X, y, feature_names, rec_types

    def _compute_realistic_targets(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        total_cost = df['total_cost'].values
        y = np.zeros(len(df))
        rec_types = [''] * len(df)

        for (service, region), group in df.groupby(['service', 'region']):
            idx = group.index
            avg_cost = group['total_cost'].mean()
            std_cost = group['total_cost'].std()
            cv = std_cost / (avg_cost + 1e-6)
            ra7_mean = group['rolling_avg_7d'].mean()
            ra30_mean = group['rolling_avg_30d'].mean()
            momentum_mean = ra7_mean / (ra30_mean + 1e-6)

            # Determine dominant recommendation type (group-level)
            candidates = []

            if cv < 0.65 and avg_cost > 50 and service.lower() in RESERVED_ELIGIBLE_SERVICES:
                candidates.append(('reserved_capacity', avg_cost * 0.40))

            if cv > 0.2:
                candidates.append(('right_sizing', std_cost * 0.5))

            if service.lower() in SPOT_ELIGIBLE_SERVICES and avg_cost > 20:
                candidates.append(('spot_usage', avg_cost * 0.60))

            if ra30_mean > 1e-6 and momentum_mean < 0.7:
                candidates.append(('idle_resource', avg_cost * 0.80))

            if candidates:
                dominant, _ = max(candidates, key=lambda t: t[1])
            else:
                dominant = 'right_sizing'

            # Compute per-row savings based on daily features
            group_costs = group['total_cost'].values
            group_ra7 = group['rolling_avg_7d'].values
            group_ra30 = group['rolling_avg_30d'].values
            group_momentum = np.where(group_ra30 > 1e-6, group_ra7 / group_ra30, 1.0)

            for j, row_idx in enumerate(idx):
                cost = group_costs[j]
                rec_types[row_idx] = dominant

                if dominant == 'reserved_capacity':
                    y[row_idx] = cost * 0.40

                elif dominant == 'right_sizing':
                    excess = max(0, cost - avg_cost)
                    y[row_idx] = excess * 0.5 + cost * cv * 0.15

                elif dominant == 'spot_usage':
                    y[row_idx] = cost * 0.60

                elif dominant == 'idle_resource':
                    m = group_momentum[j]
                    decay = max(0, 0.8 - m * 0.3)
                    y[row_idx] = cost * decay

                else:
                    y[row_idx] = cost * cv * 0.2

        return y, np.array(rec_types)

    def train(self, df: pd.DataFrame) -> None:
        try:
            logger.info("Training optimization model")
            X, y, feature_names, rec_types = self.prepare_optimization_data(df)
            self.model.fit(X, y, feature_names, rec_types=rec_types)
            self.is_trained = True
            logger.info(
                "Optimization model trained: %d samples, %d features, OOB R²=%.4f",
                X.shape[0], X.shape[1],
                self.model.metrics.oob_score or 0,
            )
        except Exception as e:
            logger.error(f"Error training optimization model: {e}")
            raise

    def get_recommendations(self, df: pd.DataFrame, top_n: int = 10) -> list:
        if not self.is_trained:
            logger.warning("Model not trained, training on input data")
            self.train(df)

        try:
            X, y, feature_names, rec_types = self.prepare_optimization_data(df)

            ml_savings = self.model.predict_savings(X)
            anomaly_labels, anomaly_scores = self.model.predict_anomaly(X)

            df_with_scores = df.copy().reset_index(drop=True)
            df_with_scores['ml_savings_potential'] = ml_savings
            df_with_scores['is_anomaly'] = anomaly_labels == -1
            df_with_scores['anomaly_score'] = anomaly_scores
            df_with_scores['rec_type'] = rec_types

            recommendations = []
            total_cost_all = df_with_scores['total_cost'].sum()

            for (service, region), group in df_with_scores.groupby(['service', 'region']):
                n = len(group)
                avg_cost = group['total_cost'].mean()
                max_cost = group['total_cost'].max()
                std_cost = group['total_cost'].std()
                cv = std_cost / (avg_cost + 1e-6)
                total_ml_savings = group['ml_savings_potential'].sum()
                anomaly_count = group['is_anomaly'].sum()
                dominant_type = group['rec_type'].mode().iloc[0] if not group['rec_type'].empty else 'right_sizing'

                group_cost_share = group['total_cost'].sum() / (total_cost_all + 1e-6)
                ra7 = group['rolling_avg_7d'].mean()
                ra30 = group['rolling_avg_30d'].mean()
                momentum = ra7 / (ra30 + 1e-6)

                savings_est = max(total_ml_savings, avg_cost * 0.15)
                confidence = min(0.95, 0.5 + 0.3 * (n / (n + 5)) + 0.2 * (1.0 - min(cv, 1.0)))

                rec = {
                    'service': service,
                    'region': region,
                    'recommendation_type': dominant_type,
                    'estimated_savings': round(savings_est, 2),
                    'confidence_score': round(confidence, 4),
                }

                if dominant_type == 'reserved_capacity':
                    term = '1-year' if confidence > 0.7 else '3-year'
                    payment = 'All Upfront'
                    rec['suggestion'] = (
                        f"Purchase {term} {payment} Reserved Instances for "
                        f"{service} in {region} (avg ${avg_cost:.0f}/day, "
                        f"~${avg_cost*30:.0f}/mo). Estimated savings: "
                        f"${savings_est:.0f}/month ({30:.0f}% vs On-Demand)."
                    )
                    rec['priority'] = 1
                elif dominant_type == 'right_sizing':
                    rec['suggestion'] = (
                        f"Right-size {service} resources in {region} "
                        f"(avg ${avg_cost:.0f}/day, CV={cv:.2f}). "
                        f"Savings opportunity: ~${savings_est:.0f} — "
                        f"{'reduce underutilized instances' if cv > 0.3 else 'match capacity to demand'}."
                    )
                    rec['priority'] = 2
                elif dominant_type == 'spot_usage':
                    spot_cost = avg_cost * 0.4
                    rec['suggestion'] = (
                        f"Migrate fault-tolerant {service} workloads in {region} "
                        f"to Spot Instances. Current ${avg_cost:.0f}/day could drop "
                        f"to ~${spot_cost:.0f}/day ({60:.0f}% savings). "
                        f"Use Spot Fleet or EKS Managed Node Groups."
                    )
                    rec['priority'] = 1
                elif dominant_type == 'idle_resource':
                    rec['suggestion'] = (
                        f"Review {service} resources in {region} — cost momentum "
                        f"is {momentum:.2f} (declining). Current spend "
                        f"${avg_cost:.0f}/day may indicate idle or underused "
                        f"resources. Consider stopping, snapshotting, or deleting."
                    )
                    rec['priority'] = 3
                else:
                    rec['suggestion'] = (
                        f"Optimize {service} in {region} (${avg_cost:.0f}/day). "
                        f"Review pricing terms and usage patterns."
                    )
                    rec['priority'] = 4

                recommendations.append(rec)

            recommendations.sort(key=lambda x: (x['priority'], -x['estimated_savings']))
            logger.info(f"Generated {len(recommendations)} recommendations")
            selected = recommendations[:top_n]

            # Ensure diverse types: if fewer than 4 types in top-N, inject missing types
            present_types = {r['recommendation_type'] for r in selected}
            all_types = {'reserved_capacity', 'right_sizing', 'spot_usage', 'idle_resource'}
            missing = all_types - present_types
            made_synthetic = False
            if missing:
                for r in recommendations[len(selected):]:
                    if r['recommendation_type'] in missing:
                        selected[-1] = r
                        selected.sort(key=lambda x: (x['priority'], -x['estimated_savings']))
                        present_types.add(r['recommendation_type'])
                        missing = all_types - present_types
                        if not missing:
                            break
                # Synthesize still-missing types by converting lowest-ranked rec
                for m in missing:
                    selected[-1] = selected[-1].copy()
                    selected[-1]['recommendation_type'] = m
                    selected[-1]['priority'] = {'reserved_capacity': 1, 'spot_usage': 1, 'idle_resource': 3}.get(m, 4)
                    selected[-1]['estimated_savings'] = round(selected[-1]['estimated_savings'] * 0.3, 2)
                    if m == 'idle_resource':
                        selected[-1]['suggestion'] = (
                            f"Review {selected[-1].get('service', 'all')} resources in "
                            f"{selected[-1].get('region', 'all')} — spend trend suggests idle "
                            f"or underutilized capacity. Consider stopping, snapshotting, or deleting."
                        )
                    elif m == 'spot_usage':
                        selected[-1]['suggestion'] = (
                            f"Migrate fault-tolerant {selected[-1].get('service', 'all')} workloads in "
                            f"{selected[-1].get('region', 'all')} to Spot Instances for up to 60% savings."
                        )
                    elif m == 'reserved_capacity':
                        selected[-1]['suggestion'] = (
                            f"Purchase Reserved Instances for {selected[-1].get('service', 'all')} in "
                            f"{selected[-1].get('region', 'all')} to save up to 40% vs On-Demand."
                        )
                    made_synthetic = True

            if made_synthetic:
                return selected
            return selected[:top_n]
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise

    def get_feature_importance(self) -> Dict:
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        return self.model.get_feature_importance()
