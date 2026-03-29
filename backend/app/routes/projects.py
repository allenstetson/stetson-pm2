from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectDetail, ProjectListResponse, ProjectSummary

router = APIRouter(tags=["projects"])


@router.get("/projects", response_model=ProjectListResponse)
def list_projects(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return"),
    q: Optional[str] = Query(default=None, description="Full-text search query"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    db: Session = Depends(get_db),
) -> ProjectListResponse:
    """
    Return a paginated list of projects, with optional full-text search and
    category filter.

    Results are ordered by project_date descending (most recent first),
    with null dates sorted last.
    """
    query = db.query(Project).filter(Project.archived == False)  # noqa: E712

    if q and q.strip():
        term = q.strip()
        tsquery = func.plainto_tsquery("english", term)
        pattern = f"%{term}%"
        query = query.filter(
            or_(
                Project.search_vector.op("@@")(tsquery),
                Project.name.ilike(pattern),
                Project.folder_name.ilike(pattern),
            )
        )

    if category and category.strip():
        query = query.filter(Project.category == category.strip())

    total = query.count()

    projects: List[Project] = (
        query
        .order_by(Project.project_date.desc().nulls_last())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return ProjectListResponse(
        items=[ProjectSummary.model_validate(p) for p in projects],
        total=total,
    )


@router.get("/projects/{project_id}", response_model=ProjectDetail)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
) -> ProjectDetail:
    """
    Return the full detail record for a single project.

    Returns 404 if the project does not exist.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectDetail.model_validate(project)
