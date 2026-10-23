from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint, false, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.models._base_entities import BaseWithPK


class CaKppMapping(BaseWithPK):
    __tablename__ = "ca_kpp_mappings"
    __table_args__ = (
        UniqueConstraint("counterparty_id", "kpp_id", name="uq_ca_kpp_mapping"),
    )

    counterparty_id: Mapped[int] = mapped_column(
        ForeignKey("shared.counterparties.id", ondelete="CASCADE"), index=True
    )
    kpp_id: Mapped[int] = mapped_column(
        ForeignKey("shared.kpps.id", ondelete="CASCADE"), index=True
    )
    is_basic: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )
    valid_from: Mapped[datetime | None] = mapped_column(DateTime)
    valid_till: Mapped[datetime | None] = mapped_column(DateTime)

    counterparty: Mapped["Counterparty"] = relationship(back_populates="kpp_list")
    kpp: Mapped["KPP"] = relationship(back_populates="ca_list")

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ({self.ca_inn}-{self.kpp_name})>'
