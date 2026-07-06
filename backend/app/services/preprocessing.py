"""
Data preprocessing and ETL pipeline.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:

    @staticmethod
    def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.copy()

            # Normalize column names
            df.columns = df.columns.str.strip()

            # ✅ Convert FIRST
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df["cost"] = pd.to_numeric(df["cost"], errors="coerce")

            if "usage_quantity" in df.columns:
                df["usage_quantity"] = pd.to_numeric(df["usage_quantity"], errors="coerce")

            # ✅ Safe string handling
            df["service"] = df["service"].astype(str).str.lower().str.strip()
            df["region"] = df["region"].fillna("unknown").astype(str).str.lower().str.strip()

            # ✅ Drop invalid rows AFTER conversion
            df = df.dropna(subset=["timestamp", "service", "cost"])

            # Remove negative costs
            df = df[df["cost"] >= 0]

            logger.info(f"✅ Cleaned data: {len(df)} rows remaining")
            return df

        except Exception as e:
            logger.error(f"Cleaning error: {e}")
            raise

    @staticmethod
    def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.copy()
            df = df.sort_values("timestamp")

            df["date"] = df["timestamp"].dt.normalize()  # ✅ FIX: Use normalize() instead of .date
            df["hour"] = df["timestamp"].dt.hour

            df["daily_cost"] = df["cost"]
            df["hourly_cost"] = df["cost"] / 24
            df["cost_velocity"] = (
                df.groupby(["service", "region"])["cost"]
                .diff()
                .fillna(0)
            )

            # Rolling averages
            df["rolling_avg_7d"] = (
                df.groupby(["service", "region"])["cost"]
                .transform(lambda x: x.rolling(7, min_periods=1).mean())
            )

            df["rolling_avg_30d"] = (
                df.groupby(["service", "region"])["cost"]
                .transform(lambda x: x.rolling(30, min_periods=1).mean())
            )

            logger.info(f"✅ Feature engineering complete: {len(df)} rows")
            return df

        except Exception as e:
            logger.error(f"❌ Feature engineering error: {e}")
            raise

    @staticmethod
    def aggregate_data(df: pd.DataFrame) -> pd.DataFrame:
        try:
            logger.info(f"📊 Before aggregation: {len(df)} rows")
            df = df.copy()

            # ✅ FIX: Ensure date is in datetime format
            if df["date"].dtype == "object":
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

            logger.info(f"Date column type: {df['date'].dtype}")

            agg_dict = {
                "cost": "sum",
                "daily_cost": "sum",
                "hourly_cost": "sum",
                "rolling_avg_7d": "mean",
                "rolling_avg_30d": "mean",
                "cost_velocity": "mean",
            }
            
            # ✅ Handle optional columns
            if "usage_quantity" in df.columns:
                agg_dict["usage_quantity"] = "sum"

            agg_df = df.groupby(["date", "service", "region"], as_index=False).agg(agg_dict)
            agg_df.rename(columns={"cost": "total_cost"}, inplace=True)

            logger.info(f"📊 After aggregation: {len(agg_df)} rows")
            logger.info(f"Aggregation columns: {list(agg_df.columns)}")
            return agg_df

        except Exception as e:
            logger.error(f"❌ Aggregation error: {e}")
            logger.error(f"DataFrame info before aggregation:\n{df.info()}")
            raise

    @staticmethod
    def full_preprocessing_pipeline(df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"🚀 Starting preprocessing pipeline with {len(df)} rows")
        df = DataPreprocessor.clean_raw_data(df)
        df = DataPreprocessor.feature_engineering(df)
        df = DataPreprocessor.aggregate_data(df)
        logger.info(f"✅ Pipeline complete: {len(df)} rows")
        return df


class DataValidator:

    @staticmethod
    def validate_cost_data(df: pd.DataFrame):
        if df is None or len(df) == 0:
            return False, "Empty dataframe"

        required_columns = ["timestamp", "service", "region", "cost"]
        missing = [c for c in required_columns if c not in df.columns]

        if missing:
            return False, f"Missing columns: {missing}"

        if df["cost"].isna().any():
            return False, "Invalid cost values"

        if (df["cost"] < 0).any():
            return False, "Negative costs found"

        if df["timestamp"].isna().any():
            return False, "Invalid timestamps"

        return True, "Valid"