from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .counterparty import Counterparty


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = {"schema": "shared"}

    id: Mapped[int] = mapped_column(primary_key=True)
    counterparty_id: Mapped[int] = mapped_column(
        ForeignKey("shared.counterparties.id"), unique=True
    )

    short_name: Mapped[str] = mapped_column(String(255))    # для UI
    code: Mapped[str | None] = mapped_column(String(50), unique=True)  # внутренний код
    description: Mapped[str | None] = mapped_column(String(1000))

    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    counterparty: Mapped[Counterparty] = relationship()
