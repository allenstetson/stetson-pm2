from sqlalchemy import BigInteger, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, PrimaryKeyConstraint

from app.models.base import Base


class Contributor(Base):
    """A person associated with one or more projects."""

    __tablename__ = "contributors"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    projects = relationship(
        "Project",
        secondary="project_contributors",
        back_populates="contributors",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Contributor id={self.id} name={self.name!r}>"


class ProjectContributor(Base):
    """Join table linking projects to contributors, with an optional role."""

    __tablename__ = "project_contributors"
    __table_args__ = (PrimaryKeyConstraint("project_id", "contributor_id"),)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    contributor_id = Column(
        BigInteger,
        ForeignKey("contributors.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Optional role description, e.g. "photographer", "editor"
    role = Column(Text, nullable=True)
