"""
SQLAlchemy DeclarativeBase with naming conventions.

The naming convention ensures Alembic autogenerate produces deterministic,
predictable constraint names across migrations, which is critical when
pgvector column types are added in later sprints.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Application-wide declarative base for all ORM models.

    Naming conventions ensure Alembic autogenerate produces
    consistent constraint names across all migrations.
    """

    __abstract__ = True

    # Explicit naming convention prevents auto-generated names
    # that vary across databases and migration runs.
    metadata = DeclarativeBase.metadata
    metadata.naming_convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
