from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.db import EntityBase, EntityStatus, CounterpartyType, CounterpartyBranch


class Counterparty(EntityBase):
    __tablename__ = "counterparties"

    name: Mapped[str] = mapped_column(String(160), index=True)
    inn: Mapped[str | None] = mapped_column(String(12), unique=True)
    opf_short: Mapped[str | None] = mapped_column(String(10))
    name_full_with_opf: Mapped[str | None] = mapped_column(String(300))

    status: Mapped[EntityStatus | None] = mapped_column(
        Enum(
            EntityStatus,
            name="entity_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
    )
    counterparty_type: Mapped[CounterpartyType | None] = mapped_column(
        Enum(
            CounterpartyType,
            name="counterparty_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
    )

    branch_type: Mapped[CounterpartyBranch | None] = mapped_column(
        Enum(
            CounterpartyBranch,
            name="counterparty_branch",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
    )

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
