from sqlalchemy import BigInteger, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from app.models.base import Base


class ProjectLink(Base):
    """An external URL associated with a project (e.g. drive folder, reference site)."""

    __tablename__ = "project_links"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    url = Column(Text, nullable=False)
    label = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    project = relationship("Project", back_populates="links")

    def __repr__(self) -> str:
        return f"<ProjectLink id={self.id} project_id={self.project_id} label={self.label!r}>"
