"""
AWS Cost Explorer integration service.
Fetches cost and usage data from AWS Cost Explorer API.
"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict

import pandas as pd

from app.core.aws_auth import create_aws_client
from app.config import AWS_COST_EXPLORER_GRANULARITY, AWS_COST_EXPLORER_DEFAULT_DAYS

logger = logging.getLogger(__name__)

# Map AWS service names to CUR product codes
SERVICE_MAP = {
    "AmazonEC2": "ec2",
    "AmazonS3": "s3",
    "AWSLambda": "lambda",
    "AmazonRDS": "rds",
    "AmazonDynamoDB": "dynamodb",
    "AmazonCloudFront": "cloudfront",
    "AmazonElastiCache": "elasticache",
    "AmazonOpenSearchService": "opensearch",
    "AmazonKinesis": "kinesis",
    "AWSSQS": "sqs",
    "AWSSNS": "sns",
    "AWSCodeBuild": "codebuild",
    "AWSCodeCommit": "codecommit",
    "AmazonAthena": "athena",
    "AWSGlue": "glue",
}


class AwsCostExplorerService:
    """Fetches cost data from AWS Cost Explorer API."""

    def __init__(
        self,
        region: str = "us-east-1",
        role_arn: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        external_id: Optional[str] = None,
    ):
        self.client = create_aws_client(
            "ce", region=region, role_arn=role_arn, access_key=access_key, secret_key=secret_key,
            external_id=external_id,
        )

    def _map_service(self, aws_name: str) -> str:
        return SERVICE_MAP.get(aws_name, aws_name.lower().replace(" ", "_"))

    def get_cost_and_usage(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        granularity: str = AWS_COST_EXPLORER_GRANULARITY,
    ) -> pd.DataFrame:
        """
        Fetch cost data from AWS Cost Explorer.
        Returns a DataFrame with columns: timestamp, service, region, cost.
        """
        if not end_date:
            end_date = date.today().strftime("%Y-%m-%d")
        if not start_date:
            start = date.today() - timedelta(days=AWS_COST_EXPLORER_DEFAULT_DAYS)
            start_date = start.strftime("%Y-%m-%d")

        logger.info(
            f"Fetching AWS Cost Explorer data from {start_date} to {end_date}"
        )

        results = []
        next_token = None

        while True:
            kwargs = {
                "TimePeriod": {"Start": start_date, "End": end_date},
                "Granularity": granularity,
                "Metrics": ["UnblendedCost", "UsageQuantity"],
                "GroupBy": [
                    {"Type": "DIMENSION", "Key": "SERVICE"},
                    {"Type": "DIMENSION", "Key": "REGION"},
                ],
            }
            if next_token:
                kwargs["NextPageToken"] = next_token

            try:
                response = self.client.get_cost_and_usage(**kwargs)
            except Exception as e:
                logger.error(f"AWS Cost Explorer API error: {e}")
                break

            for result in response.get("ResultsByTime", []):
                time_period = result["TimePeriod"]
                date_val = time_period.get("Start", start_date)

                for group in result.get("Groups", []):
                    keys = group.get("Keys", [])
                    service = self._map_service(keys[0]) if len(keys) > 0 else "unknown"
                    region = keys[1].lower() if len(keys) > 1 else "unknown"
                    amounts = group.get("Metrics", {})

                    cost_str = amounts.get("UnblendedCost", {}).get("Amount", "0")
                    usage_str = amounts.get("UsageQuantity", {}).get("Amount", "0")

                    try:
                        cost = float(cost_str)
                        usage = float(usage_str)
                    except (ValueError, TypeError):
                        cost = 0.0
                        usage = 0.0

                    if cost != 0:
                        results.append(
                            {
                                "timestamp": date_val,
                                "service": service,
                                "region": region,
                                "cost": cost,
                                "usage_quantity": usage,
                            }
                        )

            next_token = response.get("NextPageToken")
            if not next_token:
                break

        df = pd.DataFrame(results)
        logger.info(f"Fetched {len(df)} rows from AWS Cost Explorer")
        return df
