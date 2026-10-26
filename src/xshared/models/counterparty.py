from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.db import EntityBase


class Counterparty(EntityBase):
    __tablename__ = "counterparties"
    __table_args__ = (
        CheckConstraint(
            "status IS NULL OR status IN ('ACTIVE','LIQUIDATING','LIQUIDATED','BANKRUPT','REORGANIZING')",
            name="status",
        ),
        CheckConstraint(
            "counterparty_type IS NULL OR counterparty_type IN ('LEGAL','INDIVIDUAL')",
            name="counterparty_type",
        ),
        CheckConstraint(
            "branch_type IS NULL OR branch_type IN ('MAIN','BRANCH')",
            name="branch_type",
        ),
    )

    name: Mapped[str] = mapped_column(String(160), index=True)
    inn: Mapped[str | None] = mapped_column(String(12), unique=True)
    opf_short: Mapped[str | None] = mapped_column(String(10))
    name_full_with_opf: Mapped[str | None] = mapped_column(String(300))

    status: Mapped[str | None] = mapped_column(String(20))
    counterparty_type: Mapped[str | None] = mapped_column(String(20))
    branch_type: Mapped[str | None] = mapped_column(String(20))

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.counterparty_groups.id")
    )

    ogrn: Mapped[str | None] = mapped_column(String(20))
    ogrn_date: Mapped[datetime | None] = mapped_column(DateTime)

    fio_surname: Mapped[str | None] = mapped_column(String(50))
    fio_name: Mapped[str | None] = mapped_column(String(50))
    fio_patronymic: Mapped[str | None] = mapped_column(String(50))
    management_post: Mapped[str | None] = mapped_column(String(50))
    management_disqualified: Mapped[str | None] = mapped_column(String(50))
    management_name: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(150))
    address_full: Mapped[str | None] = mapped_column(String(500))

    kpp_list: Mapped[list["CaKppMapping"]] = relationship(
        back_populates='counterparty'
    )
    counterpartygroup: Mapped["CounterpartyGroup | None"] = relationship(
        back_populates="ca_list"
    )
    company: Mapped["Company | None"] = relationship(
        back_populates="counterparty",
        uselist=False,
    )
