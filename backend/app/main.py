from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy import text

from app.config import settings
from app.database import engine
import app.models  # noqa: F401 — registers all ORM models with SQLAlchemy metadata

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Home Projects API",
    description="Local-first home project and media management system",
    version="0.1.0",
)

# Add CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Verify database connection on startup."""
    if engine is not None:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("✅ Database connection successful")
        except Exception as e:
            logger.warning(f"⚠️  Database connection failed: {e}. Continuing without DB.")
    else:
        logger.warning("⚠️  Database engine not initialized")


@app.get("/health")
def get_health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Home Projects API v0.1.0"}
