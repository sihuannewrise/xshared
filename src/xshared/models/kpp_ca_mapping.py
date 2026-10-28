from datetime import datetime

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey, Index, UniqueConstraint,
    false, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.db import BaseWithPK


class KppCaMapping(BaseWithPK):
    """
    Связь контрагента с КПП.

    У одного контрагента может быть несколько КПП (обособленные подразделения).
    Один КПП — основной (is_basic = true), остальные — дополнительные.
    Период действия: valid_from / valid_till (null = бессрочно).
    """
    __tablename__ = "kpp_ca_mappings"
    __table_args__ = (
        UniqueConstraint("counterparty_id", "kpp_id", name="uq_kpp_ca_mapping"),
        CheckConstraint(
            "valid_till IS NULL OR valid_from IS NULL OR valid_till >= valid_from",
            name="period",
        ),
        Index(
            "uq_kpp_ca_mapping_basic",
            "counterparty_id",
            unique=True,
            postgresql_where=text("is_basic = true"),
        ),
    )

    counterparty_id: Mapped[int] = mapped_column(
        ForeignKey("shared.counterparties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kpp_id: Mapped[int] = mapped_column(
        ForeignKey("shared.kpps.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    is_basic: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )

    valid_from: Mapped[datetime | None] = mapped_column(DateTime)
    valid_till: Mapped[datetime | None] = mapped_column(DateTime)

    counterparty: Mapped["Counterparty"] = relationship(back_populates="kpp_list")
    kpp: Mapped["KPP"] = relationship(back_populates="ca_list")

    def __repr__(self) -> str:
        return f"<KppCaMapping (ca={self.counterparty_id}, kpp={self.kpp_id})>"
