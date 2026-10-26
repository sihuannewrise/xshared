from datetime import date

from sqlalchemy import (
    Boolean, CheckConstraint, Date, ForeignKey, String,
    UniqueConstraint, func, true
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.models._base_entities import TimestampedBase


class Employee(TimestampedBase):
    __tablename__ = "employees"
    __table_args__ = (
        UniqueConstraint("company_id", "id", name="uq_employees_company_id_id"),
        UniqueConstraint("user_id", name="uq_employees_user_id"),
        UniqueConstraint("company_id", "personnel_no", name="uq_employees_company_personnel_no"),
        CheckConstraint(
            "fired_at IS NULL OR hired_at IS NULL OR fired_at >= hired_at",
            name="period",
        ),
    )

    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.companies.id"), index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.users.id"), index=True
    )

    first_name: Mapped[str] = mapped_column(String(100))
    patronymic_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    birthdate: Mapped[date | None]
    personnel_no: Mapped[str | None] = mapped_column(String(10))
    social_no: Mapped[str | None] = mapped_column(String(20), unique=True)

    position: Mapped[str | None] = mapped_column(String(255))
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.departments.id")
    )

    hired_at: Mapped[date | None] = mapped_column(Date)
    fired_at: Mapped[date | None] = mapped_column(Date)

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(),
    )

    user: Mapped["User | None"] = relationship(
        back_populates="employee", lazy="selectin"
    )
    company: Mapped["Company | None"] = relationship(
        back_populates="employees", lazy="selectin"
    )
    department: Mapped["Department | None"] = relationship(
        back_populates="employees", lazy="selectin"
    )

    @hybrid_property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.patronymic_name]
        return " ".join(p for p in parts if p)

    @full_name.expression
    def full_name(cls):
        return func.concat_ws(
            " ",
            func.coalesce(cls.last_name, ""),
            func.coalesce(cls.first_name, ""),
            func.coalesce(cls.patronymic_name, ""),
        )
