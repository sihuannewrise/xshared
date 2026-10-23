from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.db import SharedBase


class Company(SharedBase):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    counterparty_id: Mapped[int] = mapped_column(
        ForeignKey("shared.counterparties.id"), unique=True
    )

    short_name: Mapped[str] = mapped_column(String(50))
    code: Mapped[str | None] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    counterparty: Mapped["Counterparty"] = relationship(
        back_populates="company"
    )

    def __repr__(self) -> str:
        return f"<Company ({self.short_name})>"
