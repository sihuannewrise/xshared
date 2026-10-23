from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, false, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.xshared.db import Base
from ._selectchoice import EntityStatus


class BaseWithPK(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class SupplementaryBase(BaseWithPK):
    __abstract__ = True
    name: Mapped[str] = mapped_column(String(50), unique=True)

    def __repr__(self) -> str:
        description = getattr(self, 'description', None)
        if description is not None:
            return f'<{type(self).__name__} ({self.name}-{self.description})>'
        return f'<{type(self).__name__} ({self.name})>'


class EntityBase(Base):
    __abstract__ = True

    address: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[EntityStatus | None] = mapped_column(String(20))

    actuality_date: Mapped[datetime | None]
    registration_date: Mapped[datetime | None]
    liquidation_date: Mapped[datetime | None]

    is_archived: Mapped[bool] = mapped_column(
        server_default=false(), nullable=False
    )

    def __repr__(self) -> str:
        name = getattr(self, 'name', None)
        if name is not None:
            return f'<{type(self).__name__} ({name})>'


class KPP(SupplementaryBase):
    """Справочник КПП."""

    ca_list: Mapped[list[CaKppMapping]] = relationship(
        back_populates='kpp'
    )


class CounterpartyGroup(SupplementaryBase):
    """Группа контрагентов (ЛУКОЙЛ, госорганы)."""

    ca_list: Mapped[list[Counterparty]] = relationship(
        back_populates='counterpartygroup'
    )
