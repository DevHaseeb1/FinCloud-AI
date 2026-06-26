"""
AWS integration API endpoints.
Manages AWS account connections, triggers billing data fetch,
and reads CUR reports from S3.
"""

import logging
import uuid
import time
from datetime import datetime, timedelta, date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
import pandas as pd

from app.core.database import get_db
from app.core.aws_auth import encrypt_credential, decrypt_credential, create_aws_client
from app.api.dependencies import require_authenticated_user
from app.models import db_models, schemas
from app.models.db_models import User
from app.services.aws_cost_explorer import AwsCostExplorerService
from app.services.aws_cur_reader import AwsCurReaderService
from app.services.preprocessing import DataPreprocessor
from app.services.anomaly_detection import AnomalyDetectionService
from app.services.forecasting import ForecastingService
from app.services.optimization import OptimizationService

logger = logging.getLogger(__name__)


def _decrypt(val: Optional[str]) -> Optional[str]:
    """Decrypt a credential, returning plaintext if already decrypted."""
    if val is None:
        return None
    try:
        return decrypt_credential(val)
    except Exception:
        return val

router = APIRouter(prefix="/aws", tags=["aws"])

ROLE_NAME = "FinCloudAIReadOnlyRole"


@router.get("/cloudformation-template")
def get_cloudformation_template():
    """Serve the CloudFormation template YAML."""
    import os
    template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cloudformation", "readonly-role.yaml")
    with open(template_path, "r") as f:
        return Response(f.read(), media_type="text/plain", headers={"Content-Disposition": "attachment; filename=fincloud-ai-readonly-role.yaml"})


@router.post("/connections/setup", response_model=schemas.APIResponse)
def setup_connection(
    current_user: User = Depends(require_authenticated_user),
):
    """Generate external_id, role_name, and CloudFormation URL for a new connection."""
    from app.core.settings import get_settings
    settings = get_settings()
    external_id = f"fc-{uuid.uuid4().hex[:12]}"

    download_url = "/aws/cloudformation-template"

    cloudformation_url = (
        f"https://console.aws.amazon.com/cloudformation/home"
        f"?region=us-east-1#/stacks/create"
    )

    return schemas.APIResponse(
        status="success",
        data={
            "external_id": external_id,
            "role_name": ROLE_NAME,
            "cloudformation_url": cloudformation_url,
            "template_download_url": download_url,
        },
        message="Setup credentials generated",
    )


@router.post("/connections/test", response_model=schemas.APIResponse)
def test_connection(
    req: schemas.AwsTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Validate STS AssumeRole, Cost Explorer, and CUR access."""
    conn = db.query(db_models.AwsConnection).filter(
        db_models.AwsConnection.id == req.connection_id,
        db_models.AwsConnection.user_id == current_user.id,
    ).first() if req.connection_id else None

    role_arn = req.role_arn or (_decrypt(conn.role_arn) if conn else None)
    external_id = req.external_id or (conn.external_id if conn else None)
    access_key = req.access_key_id
    secret_key = req.secret_access_key
    region = req.region or (conn.region if conn else "us-east-1")
    bucket = req.s3_cur_bucket or (conn.s3_cur_bucket if conn else None)
    prefix = req.s3_cur_prefix or (conn.s3_cur_prefix if conn else "")

    results = []

    # 1. STS AssumeRole
    sts_ok = False
    sts_message = ""
    try:
        # Create an STS client with available credentials
        sts_client = create_aws_client(
            service_name="sts",
            region=region,
            role_arn=None,
            access_key=access_key,
            secret_key=secret_key,
        )
        if role_arn:
            assume_kwargs = {
                "RoleArn": role_arn,
                "RoleSessionName": "FinCloudAITest",
            }
            if external_id:
                assume_kwargs["ExternalId"] = external_id
            assumed = sts_client.assume_role(**assume_kwargs)
            results.append(schemas.AwsTestResult(
                check="STS AssumeRole",
                status="success",
                message=f"Successfully assumed role {role_arn}",
            ))
            sts_ok = True
            creds = assumed["Credentials"]
        else:
            results.append(schemas.AwsTestResult(
                check="STS AssumeRole",
                status="success",
                message="Using direct credentials (no role ARN provided)",
            ))
            sts_ok = True
            creds = None
    except Exception as e:
        msg = str(e)
        if "Unable to locate credentials" in msg:
            msg = "Backend has no AWS credentials configured. Set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY env vars, configure ~/.aws/credentials, or use the Access Key connection method."
        results.append(schemas.AwsTestResult(
            check="STS AssumeRole",
            status="error",
            message=msg[:200],
        ))
        sts_message = str(e)

    # 2. Cost Explorer access
    if sts_ok:
        try:
            explorer = AwsCostExplorerService(
                region=region,
                role_arn=role_arn,
                access_key=access_key,
                secret_key=secret_key,
                external_id=external_id,
            )
            today_str = date.today().strftime("%Y-%m-%d")
            two_days_ago = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
            df = explorer.get_cost_and_usage(
                start_date=two_days_ago,
                end_date=today_str,
            )
            results.append(schemas.AwsTestResult(
                check="Cost Explorer access",
                status="success",
                message="Cost Explorer API responded successfully",
            ))
        except Exception as e:
            results.append(schemas.AwsTestResult(
                check="Cost Explorer access",
                status="error",
                message=str(e)[:200],
            ))

    # 3. CUR bucket access
    if sts_ok and bucket:
        try:
            reader = AwsCurReaderService(
                bucket=bucket,
                prefix=prefix,
                region=region,
                role_arn=role_arn,
                access_key=access_key,
                secret_key=secret_key,
                external_id=external_id,
            )
            objects = reader.list_cur_files()
            if objects:
                results.append(schemas.AwsTestResult(
                    check="CUR bucket access",
                    status="success",
                    message=f"Found {len(objects)} CUR file(s) in s3://{bucket}/{prefix}",
                ))
            else:
                results.append(schemas.AwsTestResult(
                    check="CUR bucket access",
                    status="warning",
                    message=f"Bucket {bucket} is accessible but no CUR files found",
                ))
        except Exception as e:
            results.append(schemas.AwsTestResult(
                check="CUR bucket access",
                status="error",
                message=str(e)[:200],
            ))
    elif sts_ok and not bucket:
        results.append(schemas.AwsTestResult(
            check="CUR bucket access",
            status="skipped",
            message="No CUR bucket configured",
        ))

    overall = "success" if all(r.status == "success" for r in results) else \
              "partial" if any(r.status == "success" for r in results) else "error"

    return schemas.APIResponse(
        status="success",
        data={
            "connection_id": req.connection_id,
            "overall_status": overall,
            "checks": [r.model_dump() for r in results],
        },
        message="Connection validation complete",
    )


@router.post("/connections", response_model=schemas.APIResponse)
def create_connection(
    req: schemas.AwsConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Register a new AWS account connection."""
    access_key_enc = None
    secret_key_enc = None
    if req.access_key_id:
        access_key_enc = encrypt_credential(req.access_key_id)
    if req.secret_access_key:
        secret_key_enc = encrypt_credential(req.secret_access_key)

    if req.role_arn:
        role_arn_enc = encrypt_credential(req.role_arn)
    else:
        role_arn_enc = None

    conn = db_models.AwsConnection(
        user_id=current_user.id,
        name=req.name,
        account_id=req.account_id,
        role_arn=role_arn_enc,
        external_id=req.external_id,
        access_key_encrypted=access_key_enc,
        secret_key_encrypted=secret_key_enc,
        region=req.region,
        s3_cur_bucket=req.s3_cur_bucket,
        s3_cur_prefix=req.s3_cur_prefix.strip() if req.s3_cur_prefix else None,
        is_active=True,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)

    logger.info(f"AWS connection created: {conn.id} ({req.name})")
    return schemas.APIResponse(
        status="success",
        data={"connection_id": conn.id},
        message=f"AWS connection '{req.name}' created successfully",
    )


@router.get("/connections", response_model=schemas.APIResponse)
def list_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """List all registered AWS connections."""
    conns = db.query(db_models.AwsConnection).filter(
        db_models.AwsConnection.user_id == current_user.id,
    ).order_by(db_models.AwsConnection.created_at.desc()).all()
    return schemas.APIResponse(
        status="success",
        data={
            "connections": [
                schemas.AwsConnectionResponse.model_validate(c).model_dump() for c in conns
            ]
        },
    )


@router.get("/connections/{conn_id}", response_model=schemas.APIResponse)
def get_connection(
    conn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Get a specific AWS connection."""
    conn = db.query(db_models.AwsConnection).filter(
        db_models.AwsConnection.id == conn_id,
        db_models.AwsConnection.user_id == current_user.id,
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return schemas.APIResponse(
        status="success",
        data={"connection": schemas.AwsConnectionResponse.model_validate(conn).model_dump()},
    )


@router.get("/connections/{conn_id}/history", response_model=schemas.APIResponse)
def get_connection_fetch_history(
    conn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Get fetch history for a connection."""
    conn = db.query(db_models.AwsConnection).filter(
        db_models.AwsConnection.id == conn_id,
        db_models.AwsConnection.user_id == current_user.id,
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    history = db.query(db_models.AwsFetchHistory).filter(
        db_models.AwsFetchHistory.connection_id == conn_id,
        db_models.AwsFetchHistory.user_id == current_user.id,
    ).order_by(db_models.AwsFetchHistory.created_at.desc()).limit(50).all()
    return schemas.APIResponse(
        status="success",
        data={
            "history": [
                schemas.AwsFetchHistoryResponse.model_validate(h).model_dump() for h in history
            ]
        },
    )


@router.put("/connections/{conn_id}", response_model=schemas.APIResponse)
def update_connection(
    conn_id: int,
    req: schemas.AwsConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Update an existing AWS connection."""
    conn = db.query(db_models.AwsConnection).filter(
        db_models.AwsConnection.id == conn_id,
        db_models.AwsConnection.user_id == current_user.id,
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    update_data = req.model_dump(exclude_unset=True)
    if req.access_key_id is not None:
        conn.access_key_encrypted = encrypt_credential(req.access_key_id)
        update_data.pop("access_key_id")
    if req.secret_access_key is not None:
        conn.secret_key_encrypted = encrypt_credential(req.secret_access_key)
        update_data.pop("secret_access_key")
    if req.role_arn is not None:
        conn.role_arn = encrypt_credential(req.role_arn)
        update_data.pop("role_arn")

    for field, value in update_data.items():
        setattr(conn, field, value)

    db.commit()
    db.refresh(conn)
    return schemas.APIResponse(
        status="success",
        data={"connection_id": conn.id},
        message="Connection updated",
    )


@router.delete("/connections/{conn_id}", response_model=schemas.APIResponse)
def delete_connection(
    conn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Delete an AWS connection."""
    conn = db.query(db_models.AwsConnection).filter(
        db_models.AwsConnection.id == conn_id,
        db_models.AwsConnection.user_id == current_user.id,
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    db.delete(conn)
    db.commit()
    return schemas.APIResponse(
        status="success",
        message="Connection deleted",
    )


@router.post("/fetch", response_model=schemas.APIResponse)
def fetch_billing_data(
    req: schemas.AwsFetchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """
    Fetch billing data from AWS for a given connection.
    Supports Cost Explorer API (default) and CUR from S3.
    Runs the full ETL + ML pipeline on fetched data.
    """
    conn = db.query(db_models.AwsConnection).filter(
        db_models.AwsConnection.id == req.connection_id,
        db_models.AwsConnection.user_id == current_user.id,
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    if not conn.is_active:
        raise HTTPException(status_code=400, detail="Connection is inactive")

    access_key = None
    secret_key = None
    if conn.access_key_encrypted:
        access_key = decrypt_credential(conn.access_key_encrypted)
    if conn.secret_key_encrypted:
        secret_key = decrypt_credential(conn.secret_key_encrypted)

    end_date = req.end_date or date.today().strftime("%Y-%m-%d")
    start_date = req.start_date or (date.today() - timedelta(days=90)).strftime("%Y-%m-%d")

    fetch_start = time.time()

    fetch_record = db_models.AwsFetchHistory(
        user_id=current_user.id,
        connection_id=conn.id,
        source="",
        start_date=datetime.strptime(start_date, "%Y-%m-%d") if isinstance(start_date, str) else start_date,
        end_date=datetime.strptime(end_date, "%Y-%m-%d") if isinstance(end_date, str) else end_date,
        rows_fetched=0,
        rows_processed=0,
        status="running",
    )
    db.add(fetch_record)
    db.commit()
    db.refresh(fetch_record)

    try:
        if req.use_cur and conn.s3_cur_bucket:
            reader = AwsCurReaderService(
                bucket=conn.s3_cur_bucket,
                prefix=conn.s3_cur_prefix or "",
                region=conn.region,
                role_arn=_decrypt(conn.role_arn),
                access_key=access_key,
                secret_key=secret_key,
            )
            df = reader.fetch_latest_cur()
            source = "CUR"
        else:
            explorer = AwsCostExplorerService(
                region=conn.region,
                role_arn=_decrypt(conn.role_arn),
                access_key=access_key,
                secret_key=secret_key,
            )
            df = explorer.get_cost_and_usage(
                start_date=start_date,
                end_date=end_date,
            )
            source = "CostExplorer"

        fetch_record.source = source

        if df.empty:
            conn.last_fetch_status = "no_data"
            fetch_record.status = "no_data"
            fetch_record.duration_seconds = time.time() - fetch_start
            db.commit()
            return schemas.APIResponse(
                status="success",
                data={"connection_id": conn.id, "rows_fetched": 0, "rows_ingested": 0},
                message=f"No data retrieved from AWS {source}",
            )

        rows_fetched = len(df)
        fetch_record.rows_fetched = rows_fetched
        logger.info(f"AWS {source} returned {rows_fetched} rows")

        processed_df = DataPreprocessor.full_preprocessing_pipeline(df)
        logger.info(f"ETL pipeline produced {len(processed_df)} rows")

        if processed_df.empty:
            conn.last_fetch_status = "etl_empty"
            fetch_record.status = "etl_empty"
            fetch_record.duration_seconds = time.time() - fetch_start
            db.commit()
            return schemas.APIResponse(
                status="success",
                data={"connection_id": conn.id, "rows_fetched": rows_fetched, "rows_ingested": 0},
                message="Data fetched but ETL pipeline produced no records",
            )

        raw_records = []
        for _, row in df.iterrows():
            raw_records.append(db_models.RawCostData(
                user_id=current_user.id,
                timestamp=pd.Timestamp(row.get("timestamp", start_date)),
                service=str(row.get("service", "unknown")),
                region=str(row.get("region", "unknown")),
                cost=float(row.get("cost", 0)),
                usage_quantity=float(row.get("usage_quantity", 0)) if "usage_quantity" in row.index else None,
                account_id=str(row.get("account_id")) if pd.notna(row.get("account_id")) else None,
                instance_type=str(row.get("instance_type")) if pd.notna(row.get("instance_type")) else None,
            ))

        db.bulk_save_objects(raw_records)
        db.commit()

        processed_records = []
        for _, row in processed_df.iterrows():
            processed_records.append(db_models.ProcessedCostData(
                user_id=current_user.id,
                date=row["date"],
                service=row["service"],
                region=row["region"],
                total_cost=row["total_cost"],
                daily_cost=row.get("daily_cost"),
                hourly_cost=row.get("hourly_cost"),
                rolling_avg_7d=row.get("rolling_avg_7d"),
                rolling_avg_30d=row.get("rolling_avg_30d"),
                cost_velocity=row.get("cost_velocity"),
                usage_quantity=row.get("usage_quantity"),
            ))

        db.bulk_save_objects(processed_records)
        db.commit()
        rows_ingested = len(processed_records)
        fetch_record.rows_processed = rows_ingested

        try:
            # Build anomaly input from raw data (before aggregation)
            anomaly_df = df[["timestamp", "service", "region"]].copy()
            anomaly_df["cost"] = df["cost"]
            anomaly_df["usage_amount"] = df["usage_quantity"] if "usage_quantity" in df.columns else 0.0
            anomaly_df["account_id"] = df["account_id"].fillna("unknown").astype(str) if "account_id" in df.columns else "unknown"
            anomaly_df["usage_type"] = df["usage_type"].fillna("unknown").astype(str) if "usage_type" in df.columns else "unknown"
            if "environment" in df.columns:
                anomaly_df["environment"] = df["environment"].fillna("unknown").astype(str)
            if "instance_type" in df.columns:
                anomaly_df["instance_type"] = df["instance_type"].fillna("unknown").astype(str)

            if len(anomaly_df) >= 10:
                anomaly_svc = AnomalyDetectionService(contamination=0.1)
                anomaly_svc.train(anomaly_df)
                anomaly_results = anomaly_svc.detect_anomalies(anomaly_df)
                anom_records = []
                for _, row in anomaly_results.iterrows():
                    anom_records.append(db_models.Anomaly(
                        user_id=current_user.id,
                        date=row["date"],
                        service=row["service"],
                        region=row["region"],
                        anomaly_score=float(row.get("anomaly_score", 0)),
                        anomaly_flag=bool(row.get("anomaly_flag", False)),
                        cost_value=float(row["cost"]),
                        explanation=f"Anomaly detected for {row['service']} in {row['region']}",
                    ))
                if anom_records:
                    db.bulk_save_objects(anom_records)
                    db.commit()
        except Exception as e:
            logger.warning(f"Anomaly detection failed during AWS fetch: {e}")

        try:
            if len(processed_df) >= 10:
                forecast_svc = ForecastingService(forecast_periods=30)
                forecast_svc.train(processed_df, service="all")
                forecast_result = forecast_svc.forecast_total_cost()
                fc_records = []
                for _, row in forecast_result.iterrows():
                    fc_records.append(db_models.Forecast(
                        user_id=current_user.id,
                        date=row["date"],
                        service="all",
                        region="all",
                        predicted_cost=float(row.get("predicted_cost", 0)),
                        lower_bound=float(row.get("lower_bound", 0)),
                        upper_bound=float(row.get("upper_bound", 0)),
                    ))
                if fc_records:
                    db.bulk_save_objects(fc_records)
                    db.commit()
        except Exception as e:
            logger.warning(f"Forecasting failed during AWS fetch: {e}")

        try:
            if len(processed_df) >= 5:
                opt_svc = OptimizationService()
                recommendations = opt_svc.get_recommendations(processed_df)
                rec_records = []
                for rec in recommendations:
                    rec_records.append(db_models.Recommendation(
                        user_id=current_user.id,
                        service=rec.get("service", "all"),
                        region=rec.get("region", "all"),
                        recommendation_type=rec.get("recommendation_type", "optimization"),
                        suggestion=rec.get("suggestion", "Optimize costs"),
                        estimated_savings=float(rec.get("estimated_savings", 0)),
                        confidence_score=float(rec.get("confidence_score", 0.5)),
                        priority=int(rec.get("priority", 1)),
                    ))
                if rec_records:
                    db.bulk_save_objects(rec_records)
                    db.commit()
        except Exception as e:
            logger.warning(f"Recommendations failed during AWS fetch: {e}")

        conn.last_fetch_at = datetime.utcnow()
        conn.last_fetch_status = "success"
        fetch_record.status = "success"
        fetch_record.duration_seconds = time.time() - fetch_start
        db.commit()

        return schemas.APIResponse(
            status="success",
            data={
                "connection_id": conn.id,
                "source": source,
                "rows_fetched": rows_fetched,
                "rows_ingested": rows_ingested,
            },
            message=f"Successfully fetched {rows_fetched} rows from AWS {source}, ingested {rows_ingested}",
        )

    except Exception as e:
        conn.last_fetch_status = f"error: {str(e)[:200]}"
        fetch_record.status = "error"
        fetch_record.error_message = str(e)[:500]
        fetch_record.duration_seconds = time.time() - fetch_start
        db.commit()
        logger.error(f"AWS data fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"AWS data fetch failed: {str(e)}")
