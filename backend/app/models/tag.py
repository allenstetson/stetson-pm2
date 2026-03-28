from sqlalchemy import BigInteger, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, PrimaryKeyConstraint

from app.models.base import Base


class Tag(Base):
    """A label that can be applied to many projects."""

    __tablename__ = "tags"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    projects = relationship(
        "Project",
        secondary="project_tags",
        back_populates="tags",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name={self.name!r}>"


class ProjectTag(Base):
    """Join table linking projects to tags."""

    __tablename__ = "project_tags"
    __table_args__ = (PrimaryKeyConstraint("project_id", "tag_id"),)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag_id = Column(
        BigInteger,
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
    )
