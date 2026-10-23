from datetime import datetime

from sqlalchemy import Boolean, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.models._base_entities import TimestampedBase


class User(TimestampedBase):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("external_id", name="uq_users_external_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    external_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(100), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    display_name: Mapped[str | None] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None]

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # У пользователя может быть несколько работников (в разных обществах)
    employees: Mapped[list["Employee"]] = relationship(back_populates="user")