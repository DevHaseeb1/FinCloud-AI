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

def _dbg(message: str, data: dict, hypothesis_id: str):
    try:
        import json, time
        payload = {
            "sessionId": "e15a98",
            "runId": "pre-fix",
            "hypothesisId": hypothesis_id,
            "location": "backend/app/api/routes/upload.py",
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open(r"c:\Users\Haseeb\Desktop\FinCloud-AI\debug-e15a98.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass


@router.post("/data", response_model=schemas.APIResponse)
async def upload_cost_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process cost data.
    
    Args:
        file: CSV file containing cost data
        db: Database session
        
    Returns:
        Upload status
    """
    try:
        _dbg(
            "Upload endpoint hit",
            {
                "filename": getattr(file, "filename", None),
                "content_type": getattr(file, "content_type", None),
            },
            "H4",
        )
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported"
            )
        
        # Read file
        contents = await file.read()
        _dbg(
            "File read complete",
            {"filename": file.filename, "bytes": len(contents)},
            "H4",
        )
        df = pd.read_csv(io.BytesIO(contents))
        
        logger.info(f"Uploaded file: {file.filename} with {len(df)} rows")
        
        # Validate data
        is_valid, message = DataValidator.validate_cost_data(df)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Data validation failed: {message}")
        
        rows_uploaded = len(df)
        
        # Save raw data to database
        for _, row in df.iterrows():
            raw_cost = db_models.RawCostData(
                timestamp=pd.to_datetime(row['timestamp']),
                service=row['service'],
                region=row['region'],
                cost=float(row['cost']),
                usage_quantity=float(row.get('usage_quantity', 0)) if pd.notna(row.get('usage_quantity')) else None,
                instance_type=row.get('instance_type'),
                account_id=row.get('account_id')
            )
            db.add(raw_cost)
        
        db.commit()
        logger.info(f"Saved {rows_uploaded} raw cost records")
        
        # Preprocess data
        processed_df = DataPreprocessor.full_preprocessing_pipeline(df)
        rows_processed = len(processed_df)
        
        # Save processed data to database
        for _, row in processed_df.iterrows():
            processed_cost = db_models.ProcessedCostData(
                date=row['date'],
                service=row['service'],
                region=row['region'],
                total_cost=float(row['total_cost']),
                daily_cost=float(row.get('daily_cost', 0)) if pd.notna(row.get('daily_cost')) else None,
                hourly_cost=float(row.get('hourly_cost', 0)) if pd.notna(row.get('hourly_cost')) else None,
                rolling_avg_7d=float(row.get('rolling_avg_7d', 0)) if pd.notna(row.get('rolling_avg_7d')) else None,
                rolling_avg_30d=float(row.get('rolling_avg_30d', 0)) if pd.notna(row.get('rolling_avg_30d')) else None,
                cost_velocity=float(row.get('cost_velocity', 0)) if pd.notna(row.get('cost_velocity')) else None,
                usage_quantity=float(row.get('usage_quantity', 0)) if pd.notna(row.get('usage_quantity')) else None
            )
            db.add(processed_cost)
        
        db.commit()
        logger.info(f"Saved {rows_processed} processed cost records")
        
        return schemas.APIResponse(
            status="success",
            data={
                "filename": file.filename,
                "rows_uploaded": rows_uploaded,
                "rows_processed": rows_processed,
                "status": "completed"
            },
            message=f"Successfully processed {rows_processed} records"
        )
    except Exception as e:
        _dbg(
            "Upload endpoint exception",
            {"type": type(e).__name__, "detail": str(e)[:500]},
            "H4",
        )
        logger.error(f"Error uploading data: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sample-data", response_model=schemas.APIResponse)
async def upload_sample_data(
    num_records: int = 1000,
    db: Session = Depends(get_db)
):
    """
    Generate and upload sample cost data for testing.
    
    Args:
        num_records: Number of sample records to generate
        db: Database session
        
    Returns:
        Upload status
    """
    try:
        from app.utils.helpers import generate_sample_cost_data
        
        logger.info(f"Generating {num_records} sample cost records")
        
        # Generate sample data
        df = generate_sample_cost_data(num_records=num_records)
        
        rows_uploaded = len(df)
        
        # Save raw data
        for _, row in df.iterrows():
            raw_cost = db_models.RawCostData(
                timestamp=row['timestamp'],
                service=row['service'],
                region=row['region'],
                cost=row['cost'],
                usage_quantity=row.get('usage_quantity'),
                instance_type=row.get('instance_type'),
                account_id=row.get('account_id')
            )
            db.add(raw_cost)
        
        db.commit()
        
        # Preprocess
        processed_df = DataPreprocessor.full_preprocessing_pipeline(df)
        rows_processed = len(processed_df)
        
        # Save processed data
        for _, row in processed_df.iterrows():
            processed_cost = db_models.ProcessedCostData(
                date=row['date'],
                service=row['service'],
                region=row['region'],
                total_cost=row['total_cost'],
                daily_cost=row.get('daily_cost'),
                hourly_cost=row.get('hourly_cost'),
                rolling_avg_7d=row.get('rolling_avg_7d'),
                rolling_avg_30d=row.get('rolling_avg_30d'),
                cost_velocity=row.get('cost_velocity'),
                usage_quantity=row.get('usage_quantity')
            )
            db.add(processed_cost)
        
        db.commit()
        
        return schemas.APIResponse(
            status="success",
            data={
                "filename": "sample_data.csv",
                "rows_uploaded": rows_uploaded,
                "rows_processed": rows_processed,
                "status": "completed"
            },
            message=f"Successfully generated and processed {rows_processed} sample records"
        )
    except Exception as e:
        logger.error(f"Error uploading sample data: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
