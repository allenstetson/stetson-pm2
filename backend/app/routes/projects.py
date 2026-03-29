from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import BackupRecord, ProjectDetail, ProjectListResponse, ProjectSummary, VisibilityUpdate

router = APIRouter(tags=["projects"])


@router.get("/projects", response_model=ProjectListResponse)
def list_projects(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return"),
    q: Optional[str] = Query(default=None, description="Full-text search query"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    changed_since_backup: Optional[bool] = Query(default=None, description="Filter to projects changed since their last backup"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
) -> ProjectListResponse:
    """
    Return a paginated list of projects, with optional full-text search and
    category filter.

    Results are ordered by project_date descending (most recent first),
    with null dates sorted last.
    """
    query = db.query(Project).filter(Project.archived == False)  # noqa: E712

    # Non-admin visitors must never see sensitive projects — not even in counts.
    is_admin = current_user is not None and current_user.role == "admin"
    if not is_admin:
        query = query.filter(Project.visibility != "sensitive")

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

    if changed_since_backup is not None:
        query = query.filter(Project.changed_since_backup == changed_since_backup)

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
    current_user: Optional[User] = Depends(get_current_user),
) -> ProjectDetail:
    """
    Return the full detail record for a single project.

    Returns 404 (not 403) for sensitive projects when the caller is not an
    admin.  A 403 would confirm the project exists; 404 reveals nothing.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    is_admin = current_user is not None and current_user.role == "admin"
    if project.visibility == "sensitive" and not is_admin:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectDetail.model_validate(project)


@router.post("/projects/{project_id}/backup", response_model=ProjectDetail)
def record_backup(
    project_id: UUID,
    body: BackupRecord,
    db: Session = Depends(get_db),
) -> ProjectDetail:
    """
    Record that a manual backup was performed.

    Sets last_backup_at to now (UTC), stores backup_host, and clears the
    changed_since_backup flag.  The flag will be re-evaluated on the next
    scan if files have been modified since this timestamp.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    project.last_backup_at = datetime.now(tz=timezone.utc)
    project.backup_host = body.backup_host
    project.changed_since_backup = False
    db.commit()
    db.refresh(project)
    return ProjectDetail.model_validate(project)


@router.patch("/projects/{project_id}/visibility", response_model=ProjectDetail)
def update_visibility(
    project_id: UUID,
    body: VisibilityUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
) -> ProjectDetail:
    """
    Update a project's visibility label.  Admin-only.

    Returns 403 unconditionally for non-admins (before checking project
    existence) to avoid leaking whether a project exists.
    """
    if current_user is None or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    project.visibility = body.visibility
    db.commit()
    db.refresh(project)
    return ProjectDetail.model_validate(project)
