from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, false, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from ._selectchoice import EntityStatus

if TYPE_CHECKING:
    from .bank_account import BankAccount, CaAccountMapping
    from .counteragent import CaKppMapping, CounterAgent
    # from .payment import (
    #     PaymentProcessing,
    #     PaymentRegister,
    #     PaymentRequest,
    # )


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

    address: Mapped[Optional[str]] = mapped_column(String(200))
    status: Mapped[Optional[EntityStatus]] = mapped_column(String(20))

    actuality_date: Mapped[Optional[datetime]]
    registration_date: Mapped[Optional[datetime]]
    liquidation_date: Mapped[Optional[datetime]]

    is_archived: Mapped[bool] = mapped_column(
        server_default=false(), nullable=False
    )

    def __repr__(self) -> str:
        name = getattr(self, 'name', None)
        if name is not None:
            return f'<{type(self).__name__} ({name})>'


class BankAccountType(SupplementaryBase):
    """основной, инвест, спецсчет."""

    accounts: Mapped[list[CaAccountMapping]] = relationship(
        back_populates='bankaccounttype'
    )


class PaymentType(SupplementaryBase):
    """контрагенту, в бюджет, инвест."""

    pr_list: Mapped[list[PaymentRequest]] = relationship(
        back_populates='paymenttype'
    )


class KFP(SupplementaryBase):
    """Код финансовой позиции."""

    pr_list: Mapped[list[PaymentRequest]] = relationship(
        back_populates='kfp'
    )


class PayerStatus(SupplementaryBase):
    """Статус плательщика."""

    pr_list: Mapped[list[PaymentRequest]] = relationship(
        back_populates='payerstatus'
    )


class KBK(SupplementaryBase):
    """КБК."""

    pr_list: Mapped[list[PaymentRequest]] = relationship(
        back_populates='kbk'
    )


class OKTMO(SupplementaryBase):
    """ОКТМО."""

    pr_list: Mapped[list[PaymentRequest]] = relationship(
        back_populates='oktmo'
    )


class Prepayment(SupplementaryBase):
    """Платёж авансовый или по факту."""

    pr_list: Mapped[list[PaymentRequest]] = relationship(
        back_populates='prepayment'
    )


class PaymentStatus(SupplementaryBase):
    """Статус платежа: у исполнителя, на подписи, на исполнении."""

    register: Mapped[list[PaymentRegister]] = relationship(
        back_populates='paymentstatus'
    )


class PaymentVerdict(SupplementaryBase):
    """Решение подписанта: согласовано, на доработку, отклонено."""

    proc: Mapped[list[PaymentProcessing]] = relationship(
        back_populates='paymentverdict'
    )


class KPP(SupplementaryBase):
    """Справочник КПП."""

    ca_list: Mapped[list[CaKppMapping]] = relationship(
        back_populates='kpp'
    )


class CounterAgentGroup(SupplementaryBase):
    """Группа контрагентов (ЛУКОЙЛ, госорганы)."""

    ca_list: Mapped[list[CounterAgent]] = relationship(
        back_populates='counteragentgroup'
    )


class Currency(SupplementaryBase):
    """Справочник валют."""

    acc_list: Mapped[list[BankAccount]] = relationship(
        back_populates='currency'
    )