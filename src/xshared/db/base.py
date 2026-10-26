from datetime import datetime

from sqlalchemy import (
    CheckConstraint, MetaData, String, false,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from xshared.db.mixins import IdMixin, TimestampMixin


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class SharedBase(DeclarativeBase):
    metadata = MetaData(schema="shared", naming_convention=NAMING_CONVENTION)


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


class EntityBase(TimestampedBase):
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
