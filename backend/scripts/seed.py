"""
Seed script — populates the database with a small set of realistic fake projects.

Run from the backend/ directory (with DATABASE_URL in the environment):

    python scripts/seed.py

Or inside the running container:

    docker exec projects_backend python scripts/seed.py
"""

import sys
import os

# Ensure backend/app is importable when script is run from backend/ directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (  # noqa: F401 — side-effect: registers all models
    Project,
    Tag,
    ProjectTag,
    Contributor,
    ProjectContributor,
    ProjectLink,
)


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


SEED_PROJECTS = [
    {
        "name": "Summer Vacation 2024",
        "category": "home",
        "folder_name": "2024_06_15_summerVacation",
        "nas_path": "/volume1/Projects/home/2024_06_15_summerVacation",
        "visibility": "family",
        "project_date": date(2024, 6, 15),
        "file_count": 342,
        "disk_usage_bytes": 4_812_005_376,  # ~4.5 GB
        "media_types": ["photo", "video"],
        "notes": "Beach trip with the whole family. Outer Banks.",
        "tags": ["vacation", "family", "beach"],
        "contributors": [
            {"name": "Stetson", "role": "photographer"},
            {"name": "Amy", "role": "photographer"},
        ],
    },
    {
        "name": "Back to School — Jonah Fall 2023",
        "category": "school",
        "folder_name": "2023_09_01_backToSchool_jonah",
        "nas_path": "/volume1/Projects/school/2023_09_01_backToSchool_jonah",
        "visibility": "family",
        "project_date": date(2023, 9, 1),
        "file_count": 28,
        "disk_usage_bytes": 187_269_120,  # ~178 MB
        "media_types": ["photo", "document"],
        "notes": "First day of middle school, supply lists, schedule.",
        "tags": ["school", "jonah"],
        "contributors": [
            {"name": "Jonah", "role": "subject"},
        ],
    },
    {
        "name": "Portfolio Website Rebuild",
        "category": "work",
        "folder_name": "2025_01_10_portfolioWebsite",
        "nas_path": "/volume1/Projects/work/2025_01_10_portfolioWebsite",
        "visibility": "work",
        "project_date": date(2025, 1, 10),
        "file_count": 91,
        "disk_usage_bytes": 52_428_800,  # ~50 MB
        "media_types": ["document"],
        "notes": "React + TypeScript personal site. Deployed to Vercel.",
        "tags": ["web", "portfolio", "react"],
        "contributors": [
            {"name": "Stetson", "role": "developer"},
        ],
        "links": [
            {"url": "https://github.com/username/portfolio", "label": "GitHub repo"},
        ],
    },
    {
        "name": "Christmas Morning 2024",
        "category": "home",
        "folder_name": "2024_12_25_christmasMorning",
        "nas_path": "/volume1/Projects/home/2024_12_25_christmasMorning",
        "visibility": "family",
        "project_date": date(2024, 12, 25),
        "file_count": 185,
        "disk_usage_bytes": 2_684_354_560,  # ~2.5 GB
        "media_types": ["photo", "video"],
        "notes": "Kids opening gifts. Fireplace. Cozy morning.",
        "tags": ["holiday", "family", "christmas"],
        "contributors": [
            {"name": "Stetson", "role": "photographer"},
            {"name": "Amy", "role": "videographer"},
        ],
        "changed_since_backup": True,
    },
    {
        "name": "Home Renovation Planning",
        "category": "home",
        "folder_name": "2024_03_15_homeRenovationPlanning",
        "nas_path": "/volume1/Projects/home/2024_03_15_homeRenovationPlanning",
        "visibility": "sensitive",
        "project_date": date(2024, 3, 15),
        "file_count": 54,
        "disk_usage_bytes": 322_961_408,  # ~308 MB
        "media_types": ["document", "photo"],
        "notes": "Quotes, floor plans, contractor contacts. Keep private.",
        "tags": ["home", "renovation", "finances"],
        "contributors": [
            {"name": "Stetson", "role": "owner"},
            {"name": "Amy", "role": "owner"},
        ],
    },
]


def get_or_create_tag(session: Session, name: str) -> Tag:
    tag = session.query(Tag).filter_by(name=name).first()
    if not tag:
        tag = Tag(name=name)
        session.add(tag)
        session.flush()
    return tag


def get_or_create_contributor(session: Session, name: str) -> Contributor:
    contrib = session.query(Contributor).filter_by(name=name).first()
    if not contrib:
        contrib = Contributor(name=name)
        session.add(contrib)
        session.flush()
    return contrib


def seed() -> None:
    if SessionLocal is None:
        print("ERROR: Database session not available. Check DATABASE_URL.")
        sys.exit(1)

    with Session(bind=SessionLocal.kw["bind"]) as session:
        existing = session.query(Project).count()
        if existing > 0:
            print(f"Database already has {existing} project(s). Skipping seed.")
            return

        print("Seeding database with sample projects...")

        for data in SEED_PROJECTS:
            project = Project(
                name=data["name"],
                category=data.get("category"),
                folder_name=data["folder_name"],
                nas_path=data["nas_path"],
                visibility=data.get("visibility", "family"),
                project_date=data.get("project_date"),
                file_count=data.get("file_count"),
                disk_usage_bytes=data.get("disk_usage_bytes"),
                media_types=data.get("media_types"),
                notes=data.get("notes"),
                changed_since_backup=data.get("changed_since_backup", False),
                last_scanned_at=utcnow(),
            )
            session.add(project)
            session.flush()  # Assigns project.id before adding relationships

            for tag_name in data.get("tags", []):
                tag = get_or_create_tag(session, tag_name)
                session.add(ProjectTag(project_id=project.id, tag_id=tag.id))

            for contrib_data in data.get("contributors", []):
                contributor = get_or_create_contributor(session, contrib_data["name"])
                session.add(
                    ProjectContributor(
                        project_id=project.id,
                        contributor_id=contributor.id,
                        role=contrib_data.get("role"),
                    )
                )

            for link_data in data.get("links", []):
                session.add(
                    ProjectLink(
                        project_id=project.id,
                        url=link_data["url"],
                        label=link_data.get("label"),
                    )
                )

            print(f"  + {project.folder_name}")

        session.commit()
        print(f"Done. Inserted {len(SEED_PROJECTS)} projects.")


if __name__ == "__main__":
    seed()
