from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy import text

from app.config import settings
from app.database import engine, SessionLocal
import app.models  # noqa: F401 — registers all ORM models with SQLAlchemy metadata
from app.auth import router as auth_router
from app.routes import projects as projects_router
from app.routes import scan as scan_router

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


app.include_router(auth_router.router, prefix="/api")
app.include_router(projects_router.router, prefix="/api")
app.include_router(scan_router.router, prefix="/api")


@app.on_event("startup")
def startup_event():
    """Verify database connection and bootstrap admin account on startup."""
    if engine is not None:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("✅ Database connection successful")
        except Exception as e:
            logger.warning(f"⚠️  Database connection failed: {e}. Continuing without DB.")
    else:
        logger.warning("⚠️  Database engine not initialized")
        return

    # Auto-seed the admin user on first run.  If the users table already has
    # any rows, we leave it alone (manual account management takes over).
    if SessionLocal is not None:
        try:
            from app.auth.utils import hash_password
            from app.models.user import User
            db = SessionLocal()
            try:
                if db.query(User).count() == 0:
                    admin = User(
                        username=settings.admin_username,
                        hashed_password=hash_password(settings.admin_password),
                        role="admin",
                    )
                    db.add(admin)
                    db.commit()
                    logger.info("✅ Admin user bootstrapped: %s", settings.admin_username)
            finally:
                db.close()
        except Exception as e:
            logger.warning("⚠️  Could not bootstrap admin user: %s", e)


@app.get("/health")
def get_health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Home Projects API v0.1.0"}
