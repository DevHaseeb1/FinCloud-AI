"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.core.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.debug
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative base for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def _sync_schema() -> None:
    """Add missing columns to existing tables to keep schema in sync with models."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    for table_name, table in Base.metadata.tables.items():
        if not inspector.has_table(table_name):
            continue
        existing = {c["name"] for c in inspector.get_columns(table_name)}
        for column in table.columns:
            if column.name not in existing:
                try:
                    col_type = column.type.compile(engine.dialect)
                    stmt = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}"
                    with engine.connect() as conn:
                        conn.execute(text(stmt))
                        conn.commit()
                    logger.info(f"Added missing column {table_name}.{column.name}")
                except Exception as e:
                    logger.warning(f"Could not add column {table_name}.{column.name}: {e}")


def init_db() -> None:
    """Initialize database by creating all tables."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    _sync_schema()
    logger.info("Database initialization complete")


def drop_db() -> None:
    """Drop all tables from database."""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("Database tables dropped")
