"""
CLI utility for managing FinCloud-AI backend.
Run: python cli.py --help
"""

import click
import pandas as pd
import logging
from datetime import datetime
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """FinCloud-AI Backend CLI"""
    pass


@cli.command()
def init_db():
    """Initialize database with tables."""
    try:
        from app.core.database import init_db as init_database
        
        click.echo("🔄 Initializing database...")
        init_database()
        click.echo("✅ Database initialized successfully")
    except Exception as e:
        click.echo(f"❌ Error initializing database: {e}", err=True)
        sys.exit(1)


@cli.command()
def drop_db():
    """Drop all database tables (DANGER!)."""
    if click.confirm("⚠️  Are you sure you want to drop all tables?"):
        try:
            from app.core.database import drop_db as drop_database
            
            click.echo("🔄 Dropping all tables...")
            drop_database()
            click.echo("✅ Database tables dropped")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    else:
        click.echo("Cancelled")


@cli.command()
@click.option('--num-records', default=1000, help='Number of sample records')
def generate_sample_data(num_records):
    """Generate sample cost data."""
    try:
        from app.utils.helpers import generate_sample_cost_data
        
        click.echo(f"🔄 Generating {num_records} sample records...")
        df = generate_sample_cost_data(num_records=num_records)
        
        # Save to CSV
        filename = f"data/raw/sample_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        
        click.echo(f"✅ Sample data saved to {filename}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', required=True, help='CSV file path')
@click.option('--user-id', default=1, help='User ID to associate data with')
def import_data(file, user_id):
    """Import cost data from CSV."""
    try:
        from app.core.database import SessionLocal
        from app.models import db_models
        from app.services.preprocessing import DataPreprocessor, DataValidator
        
        click.echo(f"🔄 Reading file: {file}...")
        df = pd.read_csv(file)
        
        click.echo(f"📊 Validating data ({len(df)} rows)...")
        is_valid, message = DataValidator.validate_cost_data(df)
        if not is_valid:
            click.echo(f"❌ Validation failed: {message}", err=True)
            sys.exit(1)
        
        click.echo("🔄 Preprocessing data...")
        raw_df = df.copy()
        processed_df = DataPreprocessor.full_preprocessing_pipeline(df)
        
        # Save to database
        db = SessionLocal()
        
        click.echo("💾 Saving raw data...")
        for _, row in raw_df.iterrows():
            raw_cost = db_models.RawCostData(
                user_id=user_id,
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
        
        click.echo("💾 Saving processed data...")
        for _, row in processed_df.iterrows():
            processed_cost = db_models.ProcessedCostData(
                user_id=user_id,
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
        db.close()
        
        click.echo(f"✅ Successfully imported {len(raw_df)} raw and {len(processed_df)} processed records")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """Check backend status."""
    try:
        from app.core.database import SessionLocal
        
        click.echo("🔍 Checking backend status...")
        
        db = SessionLocal()
        result = db.execute("SELECT 1")
        db.close()
        
        click.echo("✅ Database: Connected")
        click.echo("✅ Backend: Ready")
    except Exception as e:
        click.echo(f"❌ Database: Disconnected - {e}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version."""
    from app.core.settings import get_settings
    settings = get_settings()
    click.echo(f"FinCloud-AI Backend {settings.app_version}")


if __name__ == '__main__':
    cli()
