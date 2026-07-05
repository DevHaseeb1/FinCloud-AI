"""
AWS Cost & Usage Report (CUR) reader service.
Reads CUR files from S3 and parses them into DataFrames.
"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional

import pandas as pd

from app.core.aws_auth import create_aws_client
from app.services.preprocessing import DataPreprocessor

logger = logging.getLogger(__name__)


class AwsCurReaderService:
    """Reads AWS CUR files from S3."""

    def __init__(
        self,
        bucket: str,
        prefix: str = "",
        region: str = "us-east-1",
        role_arn: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        external_id: Optional[str] = None,
    ):
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self.s3_client = create_aws_client(
            "s3", region=region, role_arn=role_arn, access_key=access_key, secret_key=secret_key,
            external_id=external_id,
        )

    def list_cur_files(self, max_keys: int = 20) -> list:
        """List CUR files in the configured S3 bucket/prefix."""
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket, Prefix=self.prefix, MaxKeys=max_keys
        )
        files = [
            obj["Key"]
            for obj in response.get("Contents", [])
            if obj["Key"].endswith((".csv", ".parquet", ".csv.gz"))
        ]
        logger.info(f"Found {len(files)} CUR files in s3://{self.bucket}/{self.prefix}")
        return files

    def _read_csv_from_s3(self, key: str) -> pd.DataFrame:
        """Read a CSV file from S3 into a DataFrame."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            df = pd.read_csv(response["Body"], low_memory=False)
            logger.info(f"Read {len(df)} rows from {key}")
            return df
        except Exception as e:
            logger.error(f"Error reading CUR file {key}: {e}")
            return pd.DataFrame()

    def _read_parquet_from_s3(self, key: str) -> pd.DataFrame:
        """Read a Parquet file from S3 into a DataFrame."""
        try:
            import pyarrow.parquet as pq
            import io

            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            buffer = io.BytesIO(response["Body"].read())
            table = pq.read_table(buffer)
            df = table.to_pandas()
            logger.info(f"Read {len(df)} rows from {key}")
            return df
        except ImportError:
            logger.error("pyarrow is required to read parquet CUR files")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error reading parquet CUR file {key}: {e}")
            return pd.DataFrame()

    def fetch_latest_cur(self) -> pd.DataFrame:
        """Fetch and parse the most recent CUR file from S3."""
        files = self.list_cur_files()
        if not files:
            logger.warning("No CUR files found in S3")
            return pd.DataFrame()

        latest = sorted(files)[-1]
        logger.info(f"Loading latest CUR file: {latest}")

        if latest.endswith(".parquet"):
            df = self._read_parquet_from_s3(latest)
        else:
            df = self._read_csv_from_s3(latest)

        if df.empty:
            return df

        from app.api.routes.upload import map_aws_billing_columns

        df = map_aws_billing_columns(df)

        required = ["timestamp", "service", "total_cost"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            logger.warning(f"CUR file missing required columns after mapping: {missing}")
            return pd.DataFrame()

        df = df.rename(columns={"total_cost": "cost"})
        if "region" not in df.columns:
            df["region"] = "unknown"

        keep_cols = ["timestamp", "service", "region", "cost", "usage_quantity", "account_id", "usage_type", "instance_type", "line_item_type", "resource_id", "operation", "product_family", "pricing_term", "currency_code", "normalization_factor"]
        available = [c for c in keep_cols if c in df.columns]
        df = df[available]

        return df
