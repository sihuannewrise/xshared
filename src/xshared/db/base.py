from datetime import datetime

from sqlalchemy import MetaData, String, true
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from xshared.db._mixins import IdMixin, TimestampMixin, AuditMixin, SoftDeleteMixin, IsActiveMixin


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


class BaseIsAcive(BaseWithPK, IsActiveMixin):
    __abstract__ = True


class TimestampedBase(BaseIsAcive, TimestampMixin):
    __abstract__ = True


class AuditBase(AuditMixin, SoftDeleteMixin, TimestampedBase):
    __abstract__ = True


class EntityBase(AuditBase):
    __abstract__ = True

    address: Mapped[str | None] = mapped_column(String(200))
    actuality_date: Mapped[datetime | None]
    registration_date: Mapped[datetime | None]
    liquidation_date: Mapped[datetime | None]

    def __repr__(self) -> str:
        name = getattr(self, "name", None)
        if name is not None:
            return f"<{type(self).__name__} ({name})>"
        return f"<{type(self).__name__} (id={self.id})>"
