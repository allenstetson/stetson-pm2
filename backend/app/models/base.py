from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TimestampMixin:
    """Adds created_at and updated_at columns to any model."""

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
