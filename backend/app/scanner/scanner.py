"""
scanner.py — NAS project folder scanner for StetsonProjectManager.

Responsibilities
----------------
* Walk every immediate subdirectory of `projects_root`.
* Classify the top-level sub-folders as **categories** (e.g. home, school, work).
* Walk every immediate child of each category directory as a **project folder**.
* Parse a project date from the folder name using a 4-tier cascade.
* Humanize the folder name into a display-friendly project name.
* Tally file counts, disk usage, and detected media types.
* Upsert the project record: insert on first scan, update on re-scan.
* Return a ScanResult summary (created, updated, skipped, errors).

Date-parse cascade
------------------
1. ``YYYY_MM_DD`` prefix   → parsed exactly
2. ``YYYY_MM`` prefix      → day defaults to 1
3. ``YYYY`` prefix only    → year only; directory mtime used for day/month
4. Free-form (no prefix)   → directory mtime used for full date

Name humanisation
-----------------
* Strip the date prefix (everything before and including the first non-date token delimiter).
* Split remaining tokens on ``_``.
* Expand camelCase tokens (e.g. ``summerVacation`` → ``Summer Vacation``).
* Title-case and join with spaces.

Media-type detection
--------------------
Walks the project directory tree and classifies each file extension into one of:
  photo | video | document | audio | other
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.project import Project

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Media-type extension mapping
# ---------------------------------------------------------------------------

_PHOTO_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
    ".heic", ".heif", ".raw", ".cr2", ".cr3", ".nef", ".arw",
    ".dng", ".orf", ".rw2", ".psd", ".webp",
}
_VIDEO_EXTS = {
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".m4v",
    ".mpg", ".mpeg", ".3gp", ".webm", ".mts", ".m2ts",
}
_AUDIO_EXTS = {
    ".mp3", ".aac", ".wav", ".flac", ".ogg", ".m4a", ".wma", ".aiff",
}
_DOC_EXTS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".pages", ".numbers", ".key", ".txt", ".md", ".rtf",
    ".zip", ".tar", ".gz", ".7z",
}


def _classify_extension(ext: str) -> str:
    e = ext.lower()
    if e in _PHOTO_EXTS:
        return "photo"
    if e in _VIDEO_EXTS:
        return "video"
    if e in _AUDIO_EXTS:
        return "audio"
    if e in _DOC_EXTS:
        return "document"
    return "other"


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

# Patterns in order of specificity
_PAT_FULL  = re.compile(r"^(\d{4})_(\d{2})_(\d{2})(?:_|$)")   # YYYY_MM_DD
_PAT_MONTH = re.compile(r"^(\d{4})_(\d{2})(?:_|$)")            # YYYY_MM
_PAT_YEAR  = re.compile(r"^(\d{4})(?:_|$)")                    # YYYY


def parse_project_date(folder_name: str, path: Path) -> Optional[date]:
    """Return the best date estimate for a project folder."""
    m = _PAT_FULL.match(folder_name)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    m = _PAT_MONTH.match(folder_name)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), 1)
        except ValueError:
            pass

    m = _PAT_YEAR.match(folder_name)
    if m:
        try:
            mtime = path.stat().st_mtime
            dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
            return date(int(m.group(1)), dt.month, dt.day)
        except (ValueError, OSError):
            pass

    # Fallback: use directory mtime
    try:
        mtime = path.stat().st_mtime
        return datetime.fromtimestamp(mtime, tz=timezone.utc).date()
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Name humanisation
# ---------------------------------------------------------------------------

_CAMEL_RE = re.compile(r"([a-z])([A-Z])")
# Strips a leading date prefix (up to 3 underscore-separated numeric tokens)
_DATE_PREFIX_RE = re.compile(r"^\d{4}(?:_\d{2}(?:_\d{2})?)?_?")
# Strips a single trailing extension-like suffix (.pages, .dmg, …)
_EXT_SUFFIX_RE = re.compile(r"\.[a-zA-Z0-9]{1,8}$")


def humanize_name(folder_name: str) -> str:
    """Convert a raw folder name into a human-friendly display name."""
    name = _DATE_PREFIX_RE.sub("", folder_name)
    name = _EXT_SUFFIX_RE.sub("", name)

    # Split on underscores, then expand camelCase within each token.
    tokens: List[str] = []
    for raw_token in name.split("_"):
        if not raw_token:
            continue
        expanded = _CAMEL_RE.sub(r"\1 \2", raw_token)
        tokens.append(expanded)

    result = " ".join(tokens).title().strip()
    return result or folder_name


# ---------------------------------------------------------------------------
# File stats
# ---------------------------------------------------------------------------

def _collect_stats(project_path: Path):
    """Return (file_count, disk_usage_bytes, sorted media_type list, files_changed_at)."""
    file_count = 0
    disk_usage = 0
    type_set: set[str] = set()
    max_mtime: Optional[float] = None

    for root, _dirs, files in os.walk(project_path):
        for fname in files:
            fp = Path(root) / fname
            try:
                st = fp.stat()
                sz = st.st_size
                if max_mtime is None or st.st_mtime > max_mtime:
                    max_mtime = st.st_mtime
            except OSError:
                sz = 0
            file_count += 1
            disk_usage += sz
            type_set.add(_classify_extension(fp.suffix))

    files_changed_at: Optional[datetime] = None
    if max_mtime is not None:
        files_changed_at = datetime.fromtimestamp(max_mtime, tz=timezone.utc)

    return file_count, disk_usage, sorted(type_set), files_changed_at


# ---------------------------------------------------------------------------
# ScanResult
# ---------------------------------------------------------------------------

@dataclass
class ScanResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Main scan entry point
# ---------------------------------------------------------------------------

def scan_projects(root: str, db: Session, nas_root: str = "/volume1/Projects") -> ScanResult:
    """
    Scan *root* for category/project folder pairs, upsert into the database.

    Parameters
    ----------
    root:
        Absolute path the backend container can read (e.g. ``/mnt/projects``).
    db:
        Active SQLAlchemy session — caller is responsible for commit/rollback.
    nas_root:
        The canonical NAS prefix stored in ``project.nas_path`` for display.
    """
    result = ScanResult()
    root_path = Path(root)

    if not root_path.is_dir():
        result.errors.append(f"projects_root does not exist or is not a directory: {root}")
        return result

    for category_entry in sorted(root_path.iterdir()):
        if not category_entry.is_dir():
            continue
        category = category_entry.name

        for project_entry in sorted(category_entry.iterdir()):
            if not project_entry.is_dir():
                continue

            folder_name = project_entry.name
            # Build the canonical NAS path for storage
            nas_path = f"{nas_root}/{category}/{folder_name}"
            local_path = str(project_entry)

            try:
                project_date = parse_project_date(folder_name, project_entry)
                name = humanize_name(folder_name)
                file_count, disk_usage_bytes, media_types, files_changed_at = _collect_stats(project_entry)

                # Upsert on (folder_name, category)
                project = (
                    db.query(Project)
                    .filter(Project.folder_name == folder_name, Project.category == category)
                    .first()
                )

                now = datetime.now(tz=timezone.utc)

                if project is None:
                    project = Project(
                        name=name,
                        category=category,
                        folder_name=folder_name,
                        nas_path=nas_path,
                        local_path=local_path,
                        project_date=project_date,
                        file_count=file_count,
                        disk_usage_bytes=disk_usage_bytes,
                        media_types=media_types,
                        files_changed_at=files_changed_at,
                        last_scanned_at=now,
                        changed_since_backup=False,
                    )
                    db.add(project)
                    result.created += 1
                    logger.info("Created project: %s / %s", category, folder_name)
                else:
                    project.name = name
                    project.nas_path = nas_path
                    project.local_path = local_path
                    project.project_date = project_date
                    project.file_count = file_count
                    project.disk_usage_bytes = disk_usage_bytes
                    project.media_types = media_types
                    project.files_changed_at = files_changed_at
                    project.last_scanned_at = now
                    # Recompute changed_since_backup: True only when files are newer
                    # than the last recorded backup.  Never-backed-up projects stay False.
                    if project.last_backup_at is not None and files_changed_at is not None:
                        project.changed_since_backup = files_changed_at > project.last_backup_at
                    else:
                        project.changed_since_backup = False
                    result.updated += 1
                    logger.info("Updated project: %s / %s", category, folder_name)

            except Exception as exc:  # noqa: BLE001
                msg = f"{category}/{folder_name}: {exc}"
                logger.exception("Error scanning %s", msg)
                result.errors.append(msg)

    return result
