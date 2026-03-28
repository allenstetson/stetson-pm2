"""Initial schema — projects, tags, contributors, project_links.

Creates all core tables and indexes for the Home Projects application.

Key PostgreSQL features used:
  - gen_random_uuid()  — built-in UUID generation (PG 13+, no extension needed)
  - pg_trgm extension  — enables GIN trigram index for fuzzy name search
  - GENERATED ALWAYS AS ... STORED  — auto-maintained tsvector column for
    full-text search across name, notes, and folder_name

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-03-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Extensions
    # ------------------------------------------------------------------
    # pg_trgm enables GIN trigram indexes for fast substring / ILIKE
    # searches on the project name column.
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # ------------------------------------------------------------------
    # tags
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE tags (
            id          BIGSERIAL   PRIMARY KEY,
            name        TEXT        NOT NULL,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE UNIQUE INDEX idx_tags_name ON tags (name)")

    # ------------------------------------------------------------------
    # contributors
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE contributors (
            id          BIGSERIAL   PRIMARY KEY,
            name        TEXT        NOT NULL,
            email       TEXT,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    # ------------------------------------------------------------------
    # projects  (references tags / contributors via join tables below)
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE projects (
            id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            name                    TEXT        NOT NULL,
            category                TEXT,
            folder_name             TEXT        NOT NULL,
            nas_path                TEXT        NOT NULL,
            local_path              TEXT,
            visibility              TEXT        NOT NULL DEFAULT 'family',
            archived                BOOLEAN     NOT NULL DEFAULT FALSE,
            thumbnail_path          TEXT,
            notes                   TEXT,
            project_date            DATE,
            file_count              INTEGER,
            disk_usage_bytes        BIGINT,
            media_types             TEXT[],
            naming_convention_valid BOOLEAN,
            last_scanned_at         TIMESTAMPTZ,
            last_backup_at          TIMESTAMPTZ,
            backup_host             TEXT,
            changed_since_backup    BOOLEAN     NOT NULL DEFAULT FALSE,
            search_vector           TSVECTOR    GENERATED ALWAYS AS (
                to_tsvector(
                    'english',
                    coalesce(name,        '') || ' ' ||
                    coalesce(notes,       '') || ' ' ||
                    coalesce(folder_name, '')
                )
            ) STORED,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    # B-tree indexes — used for equality / range filtering
    op.execute("CREATE INDEX idx_projects_category             ON projects (category)")
    op.execute("CREATE INDEX idx_projects_archived             ON projects (archived)")
    op.execute("CREATE INDEX idx_projects_visibility           ON projects (visibility)")
    op.execute("CREATE INDEX idx_projects_project_date         ON projects (project_date)")
    op.execute("CREATE INDEX idx_projects_changed_since_backup ON projects (changed_since_backup)")
    op.execute("CREATE INDEX idx_projects_last_scanned_at      ON projects (last_scanned_at)")

    # GIN index on the generated tsvector — powers @@ full-text queries
    op.execute(
        "CREATE INDEX idx_projects_search_vector ON projects USING GIN (search_vector)"
    )

    # GIN trigram index — powers ILIKE / fuzzy name searches
    op.execute(
        "CREATE INDEX idx_projects_name_trgm ON projects USING GIN (name gin_trgm_ops)"
    )

    # GIN index on the TEXT[] array — powers @> containment (media type filter)
    op.execute(
        "CREATE INDEX idx_projects_media_types ON projects USING GIN (media_types)"
    )

    # ------------------------------------------------------------------
    # project_tags  (many-to-many join)
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE project_tags (
            project_id  UUID    NOT NULL REFERENCES projects     (id) ON DELETE CASCADE,
            tag_id      BIGINT  NOT NULL REFERENCES tags         (id) ON DELETE CASCADE,
            PRIMARY KEY (project_id, tag_id)
        )
        """
    )
    op.execute("CREATE INDEX idx_project_tags_tag_id     ON project_tags (tag_id)")
    op.execute("CREATE INDEX idx_project_tags_project_id ON project_tags (project_id)")

    # ------------------------------------------------------------------
    # project_contributors  (many-to-many join with optional role)
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE project_contributors (
            project_id      UUID    NOT NULL REFERENCES projects      (id) ON DELETE CASCADE,
            contributor_id  BIGINT  NOT NULL REFERENCES contributors  (id) ON DELETE CASCADE,
            role            TEXT,
            PRIMARY KEY (project_id, contributor_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX idx_project_contributors_contributor_id "
        "ON project_contributors (contributor_id)"
    )
    op.execute(
        "CREATE INDEX idx_project_contributors_project_id "
        "ON project_contributors (project_id)"
    )

    # ------------------------------------------------------------------
    # project_links
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE project_links (
            id          BIGSERIAL   PRIMARY KEY,
            project_id  UUID        NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
            url         TEXT        NOT NULL,
            label       TEXT,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX idx_project_links_project_id ON project_links (project_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS project_links        CASCADE")
    op.execute("DROP TABLE IF EXISTS project_contributors CASCADE")
    op.execute("DROP TABLE IF EXISTS project_tags         CASCADE")
    op.execute("DROP TABLE IF EXISTS projects             CASCADE")
    op.execute("DROP TABLE IF EXISTS contributors         CASCADE")
    op.execute("DROP TABLE IF EXISTS tags                 CASCADE")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
