from datetime import datetime

from sqlalchemy import String, false, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from xshared.db import SharedBase
from xshared.models._mixins import IdMixin, TimestampMixin


class BaseWithPK(IdMixin, SharedBase):
    __abstract__ = True


class TimestampedBase(BaseWithPK, TimestampMixin):
    __abstract__ = True


class SupplementaryBase(BaseWithPK):
    __abstract__ = True
    name: Mapped[str] = mapped_column(String(50), unique=True)

    def __repr__(self) -> str:
        description = getattr(self, "description", None)
        if description is not None:
            return f"<{type(self).__name__} ({self.name}-{description})>"
        return f"<{type(self).__name__} ({self.name})>"


class EntityBase(BaseWithPK):
    __abstract__ = True
    __table_args__ = (
        CheckConstraint(
            "status IS NULL OR status IN ('ACTIVE','LIQUIDATING','LIQUIDATED','BANKRUPT','REORGANIZING')",
            name="ck_%(table_name)s_status",
        ),
    )

    address: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str | None] = mapped_column(String(20))  # код EntityStatus
    actuality_date: Mapped[datetime | None]
    registration_date: Mapped[datetime | None]
    liquidation_date: Mapped[datetime | None]
    is_archived: Mapped[bool] = mapped_column(
        server_default=false(), nullable=False
    )

    def __repr__(self) -> str:
        name = getattr(self, "name", None)
        if name is not None:
            return f"<{type(self).__name__} ({name})>"
        return f"<{type(self).__name__} (id={self.id})>"
