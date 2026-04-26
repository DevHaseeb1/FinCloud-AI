#!/usr/bin/env python
"""
Database initialization script.
Creates all tables based on SQLAlchemy models.
"""

import os
import sys
import logging
from sqlalchemy import text

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, SessionLocal
# Import all models to register them
from app.models import db_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting database initialization...")
        init_db()
        
        # Verify connection
        db = SessionLocal()
        logger.info("Testing database connection...")
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✓ Database initialized successfully!")
        logger.info("✓ All tables created!")
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        sys.exit(1)
