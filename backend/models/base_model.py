"""
ORM model mixins providing UUIDv7 primary keys and timestamp tracking.

UUIDv7 is used over UUIDv4 because it embeds a millisecond timestamp,
making primary keys time-sortable. This gives B-tree indexes sequential
locality on INSERT (no random page splits), which is critical for tables
that will hold millions of triage sessions and agent outputs.
"""
from datetime import datetime, timezone
from uuid import UUID, uuid4

try:
    from uuid import uuid7 as _uuid7
except ImportError:  # pragma: no cover - Python fallback path
    _uuid7 = None

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


def _generate_uuid() -> UUID:
    """Generate a UUIDv7 when available, otherwise fall back to UUIDv4."""
    if _uuid7 is not None:
        return _uuid7()
    return uuid4()


class UUIDMixin:
    """Provides a UUIDv7 primary key column.

    UUIDv7 is time-sortable, giving better B-tree index locality
    than UUIDv4 for sequential INSERT workloads.
    """

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=_generate_uuid,
        sort_order=-100,
    )


class TimestampMixin:
    """Provides created_at and updated_at columns with automatic management.

    created_at is set once at INSERT time via server_default.
    updated_at is updated on every UPDATE via onupdate.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        sort_order=100,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        sort_order=101,
    )
