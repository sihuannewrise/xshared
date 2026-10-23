from datetime import datetime
from sqlalchemy import String, Boolean, func, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import SharedBase


class User(SharedBase):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("external_id", name="uq_users_external_id"),
        {"schema": "shared"},
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # ID пользователя во внешнем IdP (FerrisKey `sub` из JWT)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Отображаемые/поисковые поля (кэш из IdP, не источник истины)
    username: Mapped[str | None] = mapped_column(String(100), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    display_name: Mapped[str | None] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    employee: Mapped["Employee | None"] = relationship(
        back_populates="user", uselist=False
    )
