"""
SQLAlchemy ORM models for the Home Projects application.

Import order matters — all models must be imported before any relationship
resolution occurs so SQLAlchemy can find them by string name.
"""

from app.models.base import Base, TimestampMixin
from app.models.project import Project
from app.models.tag import Tag, ProjectTag
from app.models.contributor import Contributor, ProjectContributor
from app.models.project_link import ProjectLink
from app.models.user import User

__all__ = [
    "Base",
    "TimestampMixin",
    "Project",
    "Tag",
    "ProjectTag",
    "Contributor",
    "ProjectContributor",
    "ProjectLink",
    "User",
]
