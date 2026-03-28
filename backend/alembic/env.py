"""Alembic environment configuration.

Reads DATABASE_URL from the application settings so the same connection
string used by the FastAPI app is also used for migrations.

Usage (from the backend/ directory):
    alembic upgrade head
    alembic revision --autogenerate -m "description"
    alembic downgrade -1
"""

import os
import sys

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Add the backend directory to sys.path so "from app.xxx" imports work when
# Alembic is invoked directly from the shell inside the container.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ---------------------------------------------------------------------------
# Alembic Config object — provides access to values in alembic.ini.
# ---------------------------------------------------------------------------
config = context.config

# Override the sqlalchemy.url with the value from our app config so we never
# hard-code credentials in alembic.ini.
from app.config import settings  # noqa: E402 — must come after sys.path edit

config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base so Alembic can detect model changes for --autogenerate.
from app.models import Base  # noqa: E402

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Run migrations
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection required).

    Emits migration SQL to stdout instead of executing it directly.
    Useful for generating SQL scripts to review before applying.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (live DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
