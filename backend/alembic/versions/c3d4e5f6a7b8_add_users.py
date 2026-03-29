"""Add users table.

Stores local admin and viewer accounts used for gating sensitive project
visibility.  Authentication is JWT-based; passwords are stored as bcrypt
hashes.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE users (
            id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            username        TEXT        NOT NULL,
            hashed_password TEXT        NOT NULL,
            role            TEXT        NOT NULL DEFAULT 'viewer',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE UNIQUE INDEX idx_users_username ON users (username)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS users CASCADE")
