import uuid

from sqlalchemy import BigInteger, Boolean, Column, Computed, Date, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """
    Core project entity. Represents a single project folder discovered on the NAS.

    The ``search_vector`` column is a PostgreSQL GENERATED ALWAYS AS STORED
    tsvector — the database recomputes it automatically on every insert/update.
    It is not settable through the ORM.

    ``media_types`` is a TEXT[] array whose values are drawn from the set:
    photo | video | document | audio | other
    """

    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default="gen_random_uuid()",
        nullable=False,
    )

    # --- Identity --------------------------------------------------------
    name = Column(Text, nullable=False)
    category = Column(Text, nullable=True)        # home | school | work | free-form
    folder_name = Column(Text, nullable=False)    # raw FS folder name
    nas_path = Column(Text, nullable=False)       # full NAS path
    local_path = Column(Text, nullable=True)

    # --- Visibility / state ----------------------------------------------
    # Values: family | school | work | sensitive
    visibility = Column(Text, nullable=False, server_default="family")
    archived = Column(Boolean, nullable=False, server_default="false")
    thumbnail_path = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # --- Dates -----------------------------------------------------------
    # project_date is parsed from YYYY_MM_DD prefix in folder_name (Chunk 6)
    project_date = Column(Date, nullable=True)

    # --- Scanner-populated fields ----------------------------------------
    file_count = Column(Integer, nullable=True)
    disk_usage_bytes = Column(BigInteger, nullable=True)
    # e.g. ['photo', 'video', 'document', 'audio', 'other']
    media_types = Column(ARRAY(Text), nullable=True)
    # Populated in Chunk 9 by naming convention checker
    naming_convention_valid = Column(Boolean, nullable=True)
    last_scanned_at = Column(DateTime(timezone=True), nullable=True)
    # Timestamp of the most recently modified file inside the project directory.
    # Computed by the scanner from file mtimes; used to derive changed_since_backup.
    files_changed_at = Column(DateTime(timezone=True), nullable=True)

    # --- Backup tracking -------------------------------------------------
    last_backup_at = Column(DateTime(timezone=True), nullable=True)
    backup_host = Column(Text, nullable=True)
    changed_since_backup = Column(Boolean, nullable=False, server_default="false")

    # --- Full-text search ------------------------------------------------
    # GENERATED ALWAYS AS STORED — maintained by PostgreSQL, never set by ORM.
    # Indexes the content of name, notes, and folder_name.
    search_vector = Column(
        TSVECTOR,
        Computed(
            "to_tsvector('english',"
            " coalesce(name, '') || ' ' ||"
            " coalesce(notes, '') || ' ' ||"
            " coalesce(folder_name, ''))",
            persisted=True,
        ),
        nullable=True,
    )

    # --- Relationships ---------------------------------------------------
    tags = relationship(
        "Tag",
        secondary="project_tags",
        back_populates="projects",
        lazy="select",
    )
    contributors = relationship(
        "Contributor",
        secondary="project_contributors",
        back_populates="projects",
        lazy="select",
    )
    links = relationship(
        "ProjectLink",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r} category={self.category!r}>"
