from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models._common import EntityBase
from app.core.models._selectchoice import (
    CounterAgentBranch,
    CounterAgentType,
)

if TYPE_CHECKING:
    from ._common import CounterAgentGroup
    from .bank_account import CaAccountMapping


class Counterparty(EntityBase):
    __tablename__ = "counterparties"
    __table_args__ = {"schema": "shared"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(160), unique=True)
    inn: Mapped[Optional[str]] = mapped_column(String(12), unique=True)
    opf_short: Mapped[Optional[str]] = mapped_column(String(10))
    name_full_with_opf: Mapped[Optional[str]] = mapped_column(String(300))

    ca_type: Mapped[Optional[CounterAgentType]] = mapped_column(String(20))

    group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('counteragentgroup.id')
    )
    counteragentgroup: Mapped[Optional[CounterAgentGroup]] = relationship(
        back_populates='ca_list'
    )

    branch_type: Mapped[Optional[CounterAgentBranch]] = mapped_column(
        String(20)
    )

    ogrn: Mapped[Optional[str]] = mapped_column(String(20))
    ogrn_date: Mapped[Optional[datetime]]
    fio_surname: Mapped[Optional[str]] = mapped_column(String(50))
    fio_name: Mapped[Optional[str]] = mapped_column(String(50))
    fio_patronymic: Mapped[Optional[str]] = mapped_column(String(50))
    management_post: Mapped[Optional[str]] = mapped_column(String(50))
    management_disqualified: Mapped[Optional[str]] = mapped_column(String(50))
    management_name: Mapped[Optional[str]] = mapped_column(String(150))
    email: Mapped[Optional[str]] = mapped_column(String(150))
    address_full: Mapped[Optional[str]] = mapped_column(String(150))

    kpp_list: Mapped[list["CaKppMapping"]] = relationship(
        back_populates='ca'
    )
    bank_accounts: Mapped[list["CaAccountMapping"]] = relationship(
        back_populates='ca'
    )
    payments: Mapped[list["PaymentRequest"]] = relationship(
        back_populates='ca'
    )

    company: Mapped[Optional["Company"]] = relationship(
        back_populates='counteragent',
        uselist=False,
        cascade='all, delete-orphan',
    )
