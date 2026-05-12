"""
Data upload and preprocessing API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io
import logging

from app.core.database import get_db
from app.models import db_models, schemas
from app.services.preprocessing import DataPreprocessor, DataValidator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/data", response_model=schemas.APIResponse)
async def upload_cost_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Simplified CSV ingestion endpoint handling only 5 required columns:
    - timestamp (required)
    - service (required)
    - region (required)
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
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        # ✅ 2. READ CSV SAFELY
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        rows_before_cleaning = len(df)
        logger.info(f"📤 CSV uploaded: {rows_before_cleaning} rows")
        logger.info(f"📋 Columns: {list(df.columns)}")
        logger.info(f"📋 CSV head (first 3 rows):\n{df.head(3)}")
        logger.info(f"📋 CSV dtypes:\n{df.dtypes}")

        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded CSV is empty")

        # ✅ 3. CLEAN COLUMN NAMES (strip, lowercase)
        df.columns = df.columns.str.strip().str.lower()
        logger.info(f"✅ Cleaned column names: {list(df.columns)}")

        # ✅ 4. VALIDATE REQUIRED COLUMNS EXIST
        required_cols = ["timestamp", "service", "region", "total_cost"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing_cols}"
            )
        logger.info("✅ All required columns present")

        # ✅ 5. SELECT ONLY NEEDED COLUMNS (ignore others)
        needed_cols = ["timestamp", "service", "region", "total_cost"]
        if "usage_quantity" in df.columns:
            needed_cols.append("usage_quantity")
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
                    timestamp=row["timestamp"],
                    service=row["service"],
                    region=row["region"],
                    cost=row["total_cost"],  # Rename: total_cost → cost
                    usage_quantity=row.get("usage_quantity") if "usage_quantity" in row.index else None,
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

        # ✅ 13. DEBUG LOGS - Summary
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