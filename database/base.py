from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, false, true
from sqlalchemy import Uuid as SqlUuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class TimestampedModelMixin:
    """
    Adds timezone-aware creation and update timestamps to ORM models.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now(),
    )


class DeletableMixin:
    """
    Soft-delete support for ORM models.

    Records are marked as deleted and timestamped rather than being removed from the database.
    """

    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    deleted_on: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def mark_deleted(self) -> None:
        """
        Mark the entity as deleted and record the deletion timestamp.
        """

        if self.deleted:
            return
        self.deleted = True
        self.deleted_on = datetime.now(timezone.utc)


class ActiveMixin:
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())


class DefaultMixin:
    """
    Marks a record as a default choice within its domain.

    Only one entity per domain should typically be flagged as default, but this is enforced at the
    application layer to keep the schema simple.
    """

    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())


class BaseModel(DeletableMixin, TimestampedModelMixin, DeclarativeBase):
    """
    Declarative SQLAlchemy base for all ORM models with auditing and soft-delete support.

    Models extending this base automatically gain ``created_at``, ``updated_at``, ``deleted``, and ``deleted_on``
    fields, ensuring consistent behaviour across the schema.
    """

    id: Mapped[UUID] = mapped_column(SqlUuid, primary_key=True, default=uuid4)
