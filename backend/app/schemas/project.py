from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectSummary(BaseModel):
    """
    Flat summary of a project returned by GET /api/projects.

    Deliberately omits heavy fields (notes, search_vector, relationships)
    that are not needed for list rendering. The detail endpoint (Chunk 7)
    will return the full shape.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category: Optional[str]
    project_date: Optional[date]
    media_types: Optional[List[str]]
    visibility: str
    folder_name: str
    file_count: Optional[int]
    disk_usage_bytes: Optional[int]


class ProjectDetail(ProjectSummary):
    """
    Full project record returned by GET /api/projects/{id}.

    Extends ProjectSummary with all scalar fields. Relationship data
    (tags, contributors, links) is deferred to a later chunk.
    """

    nas_path: str
    local_path: Optional[str]
    archived: bool
    thumbnail_path: Optional[str]
    notes: Optional[str]
    naming_convention_valid: Optional[bool]
    last_scanned_at: Optional[datetime]
    last_backup_at: Optional[datetime]
    backup_host: Optional[str]
    changed_since_backup: bool
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """Paginated list of project summaries."""

    items: List[ProjectSummary]
    total: int
