from datetime import date, datetime

from sqlalchemy import (
    Boolean, CheckConstraint, Date, ForeignKey, String,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.db import SharedBase


class Employee(SharedBase):
    __tablename__ = "employees"
    __table_args__ = (
        # Для составных FK из number_assignments (номер и работник из одного общества)
        UniqueConstraint("company_id", "id", name="uq_employees_company_id_id"),
        # Один пользователь — один работник в рамках общества
        UniqueConstraint("user_id", "company_id", name="uq_employees_user_company"),
        # Табельный номер уникален в рамках общества
        UniqueConstraint("company_id", "personnel_no", name="uq_employees_company_personnel_no"),
        CheckConstraint(
            "fired_at IS NULL OR hired_at IS NULL OR fired_at >= hired_at",
            name="ck_employees_period",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("shared.companies.id"), index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.users.id"), index=True
    )

    full_name: Mapped[str] = mapped_column(String(255))
    personnel_no: Mapped[str | None] = mapped_column(String(50))
    position: Mapped[str | None] = mapped_column(String(255))
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.departments.id")
    )

    hired_at: Mapped[date | None] = mapped_column(Date)
    fired_at: Mapped[date | None] = mapped_column(Date)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User | None"] = relationship(back_populates="employees")
    company: Mapped["Company"] = relationship()
