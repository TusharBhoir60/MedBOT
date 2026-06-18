"""
Alembic async migration environment.

Uses the synchronous psycopg2 DSN (SYNC_DATABASE_URL) for Alembic
because Alembic's autogenerate tooling does not support asyncpg.
The application runtime continues to use asyncpg exclusively.

All ORM models must be imported here so Alembic's autogenerate
can detect schema changes. As models are added in future sprints,
import them in the 'Import all models' section below.
"""
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure the backend/ directory is on sys.path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.config import settings
from database.base import Base

# ── Import all models so Alembic autogenerate detects them ──────────────────
# Sprint 1: no domain models yet — Base.metadata is empty.
# Sprint 2+: import models here, e.g.:
#   from models.patient import Patient
# ────────────────────────────────────────────────────────────────────────────

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override the sqlalchemy.url from Pydantic Settings at runtime
config.set_main_option("sqlalchemy.url", settings.db.sync_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DB connection required).

    Generates SQL scripts that can be reviewed before applying.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
