from datetime import datetime

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.db import AuditBase


class User(AuditBase):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("external_id", name="uq_users_external_id"),
    )

    external_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(100), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    display_name: Mapped[str | None] = mapped_column(String(255))

    last_login_at: Mapped[datetime | None]

    employee: Mapped["Employee | None"] = relationship(
        back_populates="user", lazy="selectin", uselist=False
    )
