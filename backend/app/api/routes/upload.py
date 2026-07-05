"""
Data upload and preprocessing API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
import pandas as pd
import io
import logging
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.settings import get_settings
from app.models import db_models, schemas
from app.services.preprocessing import DataPreprocessor, DataValidator
from app.api.dependencies import require_authenticated_user
from app.models.db_models import User
from app.services.anomaly_detection import AnomalyDetectionService
from app.services.forecasting import ForecastingService
from app.services.optimization import OptimizationService

logger = logging.getLogger(__name__)

AWS_COLUMN_PRIORITIES = {
    "timestamp": [
        "line_item_usage_start_date",
        "line_item_usage_end_date",
        "identity_time_interval",
        "bill_billing_period_start_date",
        "bill_billing_period_end_date",
    ],
    "service": [
        "product_servicename",
        "product_servicecode",
        "product_product_name",
        "product_group",
        "product_group_description",
    ],
    "region": [
        "product_region",
        "product_region_code",
        "product_location",
        "product_from_region_code",
        "product_to_region_code",
        "product_availability_zone",
    ],
    "total_cost": [
        "line_item_unblended_cost",
        "line_item_blended_cost",
        "pricing_public_on_demand_cost",
        "reservation_effective_cost",
        "savings_plan_savings_plan_rate",
    ],
    "usage_quantity": [
        "line_item_usage_amount",
        "line_item_normalized_usage_amount",
        "reservation_unused_quantity",
    ],
    "account_id": [
        "line_item_usage_account_id",
        "bill_payer_account_id",
    ],
    "usage_type": [
        "line_item_usage_type",
    ],
    "instance_type": [
        "product_instance_type",
    ],
    "environment": [
        "resource_tags_user_environment",
    ],
}


def _extract_interval_start(series: pd.Series) -> pd.Series:
    return series.astype(str).str.split("/").str[0].str.strip()



def _normalize_cur_column(name: str) -> str:
    name = name.replace('/', '_').replace('-', '_').replace(' ', '_')
    result = []
    for i, c in enumerate(name):
        if c.isupper() and i > 0 and (name[i-1].islower() or name[i-1].isdigit()):
            result.append('_')
        result.append(c)
    name = ''.join(result).lower()
    while '__' in name:
        name = name.replace('__', '_')
    return name.strip('_')

def map_aws_billing_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [_normalize_cur_column(c) for c in df.columns]

    # Map prioritized AWS columns to internal column names
    for internal_col, candidates in AWS_COLUMN_PRIORITIES.items():
        if internal_col in df.columns:
            continue

        for candidate in candidates:
            if candidate in df.columns:
                if internal_col == "timestamp" and candidate == "identity_time_interval":
                    df[internal_col] = _extract_interval_start(df[candidate])
                else:
                    df = df.rename(columns={candidate: internal_col})
                break

    # Ensure downstream pipeline has a region column
    if "region" not in df.columns:
        df["region"] = "unknown"

    return df


def _run_ml_pipeline_background(user_id, processed_json, raw_json):
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        processed_df = pd.read_json(processed_json)
        df = pd.read_json(raw_json)
        cutoff = processed_df["date"].min() if not processed_df.empty else datetime(2020, 1, 1)
        logger.info("ML pipeline starting in background...")
        db.query(db_models.Anomaly).filter(db_models.Anomaly.user_id == user_id, db_models.Anomaly.date >= cutoff).delete()
        db.query(db_models.Forecast).filter(db_models.Forecast.user_id == user_id).delete()
        db.query(db_models.Recommendation).filter(db_models.Recommendation.user_id == user_id).delete()
        db.commit()
        logger.info("Cleared old predictions")
        try:
            logger.info("Running anomaly detection...")
            svc = AnomalyDetectionService(contamination=0.1)
            adf = df[["timestamp", "service", "region"]].copy()
            adf["cost"] = df["total_cost"]
            adf["usage_amount"] = df["usage_quantity"] if "usage_quantity" in df.columns else 0.0
            adf["account_id"] = df["account_id"].fillna("unknown").astype(str) if "account_id" in df.columns else "unknown"
            adf["usage_type"] = df["usage_type"].fillna("unknown").astype(str) if "usage_type" in df.columns else "unknown"
            if len(adf) >= 10:
                svc.train(adf)
                ar = svc.detect_anomalies(adf)
                recs = [db_models.Anomaly(user_id=user_id, date=r["date"], service=r["service"], region=r["region"], anomaly_score=float(r.get("anomaly_score",0)), anomaly_flag=bool(r.get("anomaly_flag",False)), cost_value=float(r["cost"])) for _,r in ar.iterrows()]
                if recs:
                    db.bulk_save_objects(recs)
                    db.commit()
                    logger.info("Saved " + str(len(recs)) + " anomaly records")
        except Exception as e:
            logger.error("Anomaly failed: " + str(e))
        try:
            logger.info("Running forecasting...")
            fc = ForecastingService(forecast_periods=30)
            if len(processed_df) >= 10:
                fc.train(processed_df, service="all")
                fr = fc.forecast_total_cost()
                recs = [db_models.Forecast(user_id=user_id, date=r["date"], service="all", region="all", predicted_cost=float(r.get("predicted_cost",0)), lower_bound=float(r.get("lower_bound",0)), upper_bound=float(r.get("upper_bound",0))) for _,r in fr.iterrows()]
                if recs:
                    db.bulk_save_objects(recs)
                    db.commit()
                    logger.info("Saved " + str(len(recs)) + " forecast records")
        except Exception as e:
            logger.error("Forecast failed: " + str(e))
        try:
            logger.info("Generating recommendations...")
            if len(processed_df) >= 5:
                os = OptimizationService()
                recs_in = os.get_recommendations(processed_df)
                recs = [db_models.Recommendation(user_id=user_id, service=r.get("service","all"), region=r.get("region","all"), recommendation_type=r.get("recommendation_type","optimization"), suggestion=r.get("suggestion","Optimize costs"), estimated_savings=float(r.get("estimated_savings",0)), confidence_score=float(r.get("confidence_score",0.5)), priority=int(r.get("priority",1))) for r in recs_in]
                if recs:
                    db.bulk_save_objects(recs)
                    db.commit()
                    logger.info("Saved " + str(len(recs)) + " recommendation records")
        except Exception as e:
            logger.error("Recommendation failed: " + str(e))
        logger.info("ML pipeline completed")
    except Exception as e:
        logger.error("Background ML failed: " + str(e))
    finally:
        db.close()


router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/data", response_model=schemas.APIResponse)
async def upload_cost_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    settings = Depends(get_settings),
    current_user: User = Depends(require_authenticated_user),
):
    """
    Simplified CSV ingestion endpoint handling only 5 required columns:
    - timestamp (required)
    - service (required)
    - region (optional, filled with 'unknown' when missing)
    - total_cost (required, renamed to 'cost' for DB)
    - usage_quantity (optional)
    
    All other columns are ignored.
    
    Features:
    - Cleans column names (strip, lowercase)
    - Validates required columns
    - Parses timestamp with format "%m/%d/%Y %H:%M"
    - Converts total_cost → cost for DB compatibility
    - Fills missing region with "unknown"
    - Safely converts types (handles NaN, invalid values)
    - Drops invalid rows instead of crashing
    - Bulk inserts with rollback on failure
    - Comprehensive debug logging
    """
    rows_before_cleaning = 0
    try:
        # ✅ 1. VALIDATE FILE TYPE
        filename = file.filename.lower()
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        if ext not in settings.allowed_file_extensions:
            raise HTTPException(status_code=400, detail="Only CSV or Excel files are supported")

        # ✅ 2. READ FILE SAFELY
        contents = await file.read()
        if filename.endswith(".csv"):
            try:
                df = pd.read_csv(io.BytesIO(contents), encoding="utf-8-sig", dtype=str)
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(contents), encoding="latin-1", dtype=str)
        else:
            df = pd.read_excel(io.BytesIO(contents), dtype=str)

        rows_before_cleaning = len(df)
        logger.info(f"📤 File uploaded: {rows_before_cleaning} rows")
        logger.info(f"📋 Columns: {list(df.columns)}")
        logger.info(f"📋 File head (first 3 rows):\n{df.head(3)}")
        logger.info(f"📋 File dtypes:\n{df.dtypes}")

        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # ✅ 3. CLEAN COLUMN NAMES (strip, lowercase)
        df = map_aws_billing_columns(df)
        logger.info(f"✅ Cleaned and mapped column names: {list(df.columns)}")

        # ✅ 4. VALIDATE REQUIRED COLUMNS EXIST
        required_cols = ["timestamp", "service", "total_cost"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing_cols}"
            )
        logger.info("✅ Required AWS billing columns are present")

        # Ensure region is always available for downstream DB and analytics
        if "region" not in df.columns:
            df["region"] = "unknown"

        # ✅ 5. SELECT ONLY NEEDED COLUMNS (ignore others)
        needed_cols = ["timestamp", "service", "region", "total_cost", "account_id", "usage_type", "instance_type"]
        for col in ["usage_quantity", "environment"]:
            if col in df.columns:
                needed_cols.append(col)
        df = df[needed_cols].copy()
        logger.info(f"✅ Selected columns: {list(df.columns)}")

        # ✅ 6. PARSE TIMESTAMP EXPLICITLY with required format
        logger.info(f"📋 RAW timestamp values (first 5): {df['timestamp'].head(5).tolist()}")
        logger.info(f"📋 Timestamp dtype: {df['timestamp'].dtype}")

        # Keep original strings for fallback parsing
        raw_timestamps = df["timestamp"].astype(str)

        # Try the exact required format first
        df["timestamp"] = pd.to_datetime(
            raw_timestamps,
            format="%m/%d/%Y %H:%M",
            errors="coerce"
        )
        strict_valid = df["timestamp"].notna().sum()
        strict_invalid = df["timestamp"].isna().sum()

        if strict_invalid > 0:
            logger.warning(f"⚠️  {strict_invalid} rows did not match format MM/DD/YYYY HH:MM. Falling back to ISO/inferred parsing.")
            fallback_idx = df["timestamp"].isna()
            df.loc[fallback_idx, "timestamp"] = pd.to_datetime(
                raw_timestamps[fallback_idx],
                errors="coerce"
            )

        valid_timestamps = df["timestamp"].notna().sum()
        invalid_timestamps = df["timestamp"].isna().sum()
        logger.info(f"✅ Parsed timestamps after fallback: {valid_timestamps} valid, {invalid_timestamps} invalid")
        logger.info(f"📋 Parsed timestamp sample (first 5): {df['timestamp'].head(5).tolist()}")

        if invalid_timestamps > 0:
            logger.warning(f"⚠️  {invalid_timestamps} rows still have invalid timestamps after fallback parsing")
            invalid_sample = df[df["timestamp"].isna()].head(5)
            logger.warning(f"📋 Sample invalid rows after timestamp parsing fallback:\n{invalid_sample}")

        # ✅ 7. FILL MISSING REGION with "unknown"
        df["region"] = df["region"].fillna("unknown").astype(str)
        logger.info("✅ Filled missing regions with 'unknown'")

        # ✅ 8. CONVERT TYPES SAFELY
        def safe_float(val):
            """Convert value to float, return None if invalid or NaN"""
            try:
                if pd.isna(val):
                    return None
                f = float(val)
                if pd.isna(f):
                    return None
                return f
            except (ValueError, TypeError):
                return None

        # Convert total_cost to float
        logger.info(f"📋 Sample total_cost values before conversion: {df['total_cost'].head(3).tolist()}")
        df["total_cost"] = df["total_cost"].apply(safe_float)
        logger.info(f"📋 Sample total_cost values after conversion: {df['total_cost'].head(3).tolist()}")

        # Convert usage_quantity safely if present
        if "usage_quantity" in df.columns:
            logger.info(f"📋 Sample usage_quantity before conversion: {df['usage_quantity'].head(3).tolist()}")
            df["usage_quantity"] = df["usage_quantity"].apply(safe_float)
            logger.info(f"📋 Sample usage_quantity after conversion: {df['usage_quantity'].head(3).tolist()}")

        # Convert service and region to lowercase strings
        logger.info(f"📋 Sample service before lowercase: {df['service'].head(3).tolist()}")
        logger.info(f"📋 Sample region before lowercase: {df['region'].head(3).tolist()}")
        df["service"] = df["service"].astype(str).str.strip().str.lower()
        df["region"] = df["region"].astype(str).str.strip().str.lower()
        logger.info(f"📋 Sample service after lowercase: {df['service'].head(3).tolist()}")
        logger.info(f"📋 Sample region after lowercase: {df['region'].head(3).tolist()}")

        logger.info("✅ Type conversion complete")

        # ✅ 9. DROP INVALID ROWS (missing timestamp, service, or cost)
        initial_count = len(df)
        logger.info(f"🔍 Before filtering: {initial_count} rows")
        
        # Show data state BEFORE filtering
        logger.info(f"📋 DataFrame dtypes:\n{df.dtypes}")
        logger.info(f"📋 DataFrame head:\n{df.head(3)}")
        logger.info(f"📋 DataFrame null counts:\n{df.isnull().sum()}")
        
        # Check which rows will be dropped
        invalid_timestamp = df["timestamp"].isna().sum()
        invalid_service = df["service"].isna().sum() + (df["service"].astype(str).str.strip() == "").sum()
        invalid_cost = df["total_cost"].isna().sum()
        
        logger.info(f"   Invalid timestamps: {invalid_timestamp}")
        logger.info(f"   Invalid services: {invalid_service}")
        logger.info(f"   Invalid costs: {invalid_cost}")
        
        # Show sample of data that will be dropped
        if invalid_timestamp > 0:
            bad_ts = df[df["timestamp"].isna()][["timestamp", "service", "total_cost"]].head(3)
            logger.warning(f"📋 Sample of rows with invalid timestamp:\n{bad_ts}")
        
        df = df.dropna(subset=["timestamp", "service", "total_cost"])
        df = df[df["service"].astype(str).str.strip() != ""]
        df = df[df["total_cost"].notna()]
        
        rows_after_cleaning = len(df)
        rows_dropped = initial_count - rows_after_cleaning

        logger.info(f"✅ Dropped {rows_dropped} invalid rows")
        logger.info(f"📊 Rows after cleaning: {initial_count} → {rows_after_cleaning}")

        if df.empty:
            logger.error(f"❌ No valid rows remaining after cleaning! Original: {rows_before_cleaning}, Dropped: {rows_dropped}")
            raise HTTPException(status_code=400, detail=f"No valid data after cleaning. Timestamp errors: {invalid_timestamp}, Service errors: {invalid_service}, Cost errors: {invalid_cost}")

        # ✅ 10. PREPARE SQLALCHEMY OBJECTS SAFELY
        raw_records = []
        skipped_rows = 0

        for idx, row in df.iterrows():
            try:
                record = db_models.RawCostData(
                    user_id=current_user.id,
                    timestamp=row["timestamp"],
                    service=row["service"],
                    region=row["region"],
                    cost=row["total_cost"],
                    usage_quantity=row.get("usage_quantity") if "usage_quantity" in row.index else None,
                    account_id=str(row.get("account_id")) if "account_id" in row.index and pd.notna(row.get("account_id")) else None,
                    instance_type=str(row.get("instance_type")) if "instance_type" in row.index and pd.notna(row.get("instance_type")) else None,
                )
                raw_records.append(record)
            except Exception as e:
                skipped_rows += 1
                logger.warning(f"⚠️  Row {idx}: Skipped due to {type(e).__name__}: {e}")

        if skipped_rows > 0:
            logger.warning(f"⚠️  Skipped {skipped_rows} rows during object creation")

        if not raw_records:
            raise HTTPException(status_code=400, detail="No valid records after processing")

        # ✅ 11. BUILD PROCESSED DATA FROM CLEAN RAW DATA
        processed_input = df.rename(columns={"total_cost": "cost"})
        processed_df = DataPreprocessor.full_preprocessing_pipeline(processed_input)
        logger.info(f"📊 Processed data shape: {processed_df.shape}")
        logger.info(f"📋 Processed data columns: {list(processed_df.columns)}")
        logger.info("📋 Processed data sample:\n%s", processed_df.head(3))

        processed_records = []
        for idx, row in processed_df.iterrows():
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
                usage_quantity=row.get("usage_quantity") if "usage_quantity" in row.index else None,
            ))

        if not processed_records:
            raise HTTPException(status_code=500, detail="Processed data pipeline returned no records")

        # ✅ 12. BULK INSERT WITH ERROR HANDLING FOR RAW + PROCESSED DATA
        try:
            db.bulk_save_objects(raw_records)
            db.bulk_save_objects(processed_records)
            db.commit()
            rows_inserted = len(raw_records)
            processed_rows_inserted = len(processed_records)
            logger.info(f"✅ Inserted {rows_inserted} rows into raw_cost_data")
            logger.info(f"✅ Inserted {processed_rows_inserted} rows into processed_cost_data")
        except Exception as insert_error:
            db.rollback()
            logger.error(f"❌ Bulk insert failed: {insert_error}")
            raise HTTPException(status_code=500, detail=f"Database insertion failed: {str(insert_error)}")

        # 13. RUN ML MODELS IN BACKGROUND
        ml_status = {"anomaly": "processing", "forecast": "processing", "recommendation": "processing"}
        background_tasks.add_task(
            _run_ml_pipeline_background,
            user_id=current_user.id,
            processed_json=processed_df.to_json(),
            raw_json=df.to_json(),
        )
        logger.info("ML pipeline dispatched to background task")


        logger.info(f"📋 CSV Ingestion Summary:")
        logger.info(f"   Rows loaded: {rows_before_cleaning}")
        logger.info(f"   Rows after cleaning: {rows_after_cleaning}")
        logger.info(f"   Raw rows inserted: {rows_inserted}")
        logger.info(f"   Processed rows inserted: {processed_rows_inserted}")

        return schemas.APIResponse(
            status="success",
            data={
                "filename": file.filename,
                "rows_loaded": rows_before_cleaning,
                "rows_after_cleaning": rows_after_cleaning,
                "rows_inserted": rows_inserted,
                "processed_rows_inserted": processed_rows_inserted,
                "rows_ingested": rows_inserted,
            },
            message=f"Successfully ingested {rows_inserted} raw records and {processed_rows_inserted} processed records",
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ CSV ingestion failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"CSV ingestion failed: {str(e)}")