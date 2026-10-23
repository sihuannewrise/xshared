from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models._common import BaseWithPK


class CaKppMapping(BaseWithPK):
    ca_inn: Mapped[int] = mapped_column(ForeignKey('counteragent.inn'))
    kpp_name: Mapped[int] = mapped_column(ForeignKey('kpp.name'))
    is_basic: Mapped[Optional[bool]] = mapped_column(
        server_default=text('FALSE'))
    valid_from: Mapped[Optional[datetime]]
    valid_till: Mapped[Optional[datetime]]

    __table_args__ = (
        UniqueConstraint('ca_inn', 'kpp_name', name='uq_inn_kpp_mapping'),)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ({self.ca_inn}-{self.kpp_name})>'
