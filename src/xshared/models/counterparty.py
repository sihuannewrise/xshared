from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.models._base_entities import EntityBase


class Counterparty(EntityBase):
    __tablename__ = "counterparties"
    __table_args__ = (
        CheckConstraint(
            "status IS NULL OR status IN ('ACTIVE','LIQUIDATING','LIQUIDATED','BANKRUPT','REORGANIZING')",
            name="ck_counterparties_status",
        ),
    )

    name: Mapped[str] = mapped_column(String(160), unique=True)
    inn: Mapped[str | None] = mapped_column(String(12), unique=True)
    opf_short: Mapped[str | None] = mapped_column(String(10))
    name_full_with_opf: Mapped[str | None] = mapped_column(String(300))

    ca_type: Mapped[str | None] = mapped_column(String(20))  # код CounterpartyType

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.counterparty_groups.id")
    )
    counterpartygroup: Mapped["CounterpartyGroup | None"] = relationship(
        back_populates="ca_list"
    )

    branch_type: Mapped[str | None] = mapped_column(String(20))  # код CounterpartyBranch

    ogrn: Mapped[str | None] = mapped_column(String(20))
    ogrn_date: Mapped[datetime | None]
    fio_surname: Mapped[str | None] = mapped_column(String(50))
    fio_name: Mapped[str | None] = mapped_column(String(50))
    fio_patronymic: Mapped[str | None] = mapped_column(String(50))
    management_post: Mapped[str | None] = mapped_column(String(50))
    management_disqualified: Mapped[str | None] = mapped_column(String(50))
    management_name: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(150))
    address_full: Mapped[str | None] = mapped_column(String(150))

    # TODO: раскомментировать, когда появятся модели CaKppMapping / CaAccountMapping
    # kpp_list: Mapped[list["CaKppMapping"]] = relationship(back_populates="counterparty")
    # bank_accounts: Mapped[list["CaAccountMapping"]] = relationship(back_populates="counterparty")

    company: Mapped["Company | None"] = relationship(
        back_populates="counterparty",
        uselist=False,
    )
