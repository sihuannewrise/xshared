from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._common import EntityBase
from ._selectchoice import (
    CounterpartyType,
    CounterpartyBranch,
)


class Counterparty(EntityBase):
    __tablename__ = "counterparties"
    __table_args__ = {"schema": "shared"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(160), unique=True)
    inn: Mapped[str | None] = mapped_column(String(12), unique=True)
    opf_short: Mapped[Optional[str]] = mapped_column(String(10))
    name_full_with_opf: Mapped[Optional[str]] = mapped_column(String(300))

    ca_type: Mapped[Optional[CounterpartyType]] = mapped_column(String(20))

    group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('counteragentgroup.id')
    )
    counterpartygroup: Mapped[Optional[CounterpartyGroup]] = relationship(
        back_populates='ca_list'
    )

    branch_type: Mapped[Optional[CounterpartyBranch]] = mapped_column(
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
        back_populates='counterparty'
    )
    bank_accounts: Mapped[list["CaAccountMapping"]] = relationship(
        back_populates='counterparty'
    )

    company: Mapped[Optional["Company"]] = relationship(
        back_populates='counterparty',
        uselist=False,
        cascade='all, delete-orphan',
    )
