from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.scanner import ScanResult, scan_projects

router = APIRouter(tags=["scan"])


class ScanResponse(BaseModel):
    created: int
    updated: int
    skipped: int
    errors: list[str]


@router.post("/scan", response_model=ScanResponse, status_code=200)
def trigger_scan(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ScanResponse:
    """
    Trigger a full scan of the projects root directory.

    Walks every category sub-folder, upserts project records, and returns
    a summary of how many projects were created, updated, or errored.
    """
    result: ScanResult = scan_projects(
        root=settings.projects_root,
        db=db,
        nas_root=settings.nas_root,
    )

    if result.errors and result.created == 0 and result.updated == 0:
        # Entire scan failed (e.g. root directory missing)
        raise HTTPException(status_code=500, detail=result.errors[0])

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ScanResponse(
        created=result.created,
        updated=result.updated,
        skipped=result.skipped,
        errors=result.errors,
    )
