from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, declared_attr


class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

class AuditMixin:
    @declared_attr
    def created_by(cls) -> Mapped[int | None]:
        return mapped_column(
            ForeignKey("shared.users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )

    @declared_attr
    def updated_by(cls) -> Mapped[int | None]:
        return mapped_column(
            ForeignKey("shared.users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column()
    deleted_by: Mapped[int | None] = mapped_column(ForeignKey("shared.users.id", ondelete="SET NULL"))
