from datetime import date
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


class ProjectListResponse(BaseModel):
    """Paginated list of project summaries."""

    items: List[ProjectSummary]
    total: int
