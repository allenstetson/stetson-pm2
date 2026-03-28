from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import logging

from app.config import settings
from app.models.base import Base  # noqa: F401 — re-exported for Alembic

logger = logging.getLogger(__name__)

try:
    # Create the database engine
    engine = create_engine(
        settings.database_url,
        echo=False,  # Set to True for SQL debugging
    )

    # Create a session factory
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
except Exception as e:
    logger.warning(f"Failed to create database engine: {e}")
    engine = None
    SessionLocal = None


def get_db() -> Session:
    """Dependency to get a database session."""
    if SessionLocal is None:
        raise RuntimeError("Database session not available")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
