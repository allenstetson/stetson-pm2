from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectDetail, ProjectListResponse, ProjectSummary

router = APIRouter(tags=["projects"])


@router.get("/projects", response_model=ProjectListResponse)
def list_projects(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return"),
    db: Session = Depends(get_db),
) -> ProjectListResponse:
    """
    Return a paginated list of all projects.

    Results are ordered by project_date descending (most recent first),
    with null dates sorted last.
    """
    base_query = db.query(Project).filter(Project.archived == False)  # noqa: E712

    total = base_query.count()

    projects: List[Project] = (
        base_query
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
