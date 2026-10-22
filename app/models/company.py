from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

from .counterparty import Counterparty


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = {"schema": "shared"}

    id: Mapped[int] = mapped_column(primary_key=True)
    counterparty_id: Mapped[int] = mapped_column(
        ForeignKey("shared.counterparties.id"), unique=True
    )

    short_name: Mapped[str] = mapped_column(String(50))
    code: Mapped[str | None] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))


    def __repr__(self) -> str:
        return f'<Company ({self.short_name})>'

    counterparty: Mapped[Counterparty] = relationship(
        back_populates='company'
    )
