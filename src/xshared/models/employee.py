from datetime import date, datetime
from sqlalchemy import (
    String, Boolean, Date, ForeignKey, ForeignKeyConstraint,
    UniqueConstraint, CheckConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.models.base import SharedBase


class Employee(SharedBase):
    __tablename__ = "employees"
    __table_args__ = (
        # Для составных FK из number_assignments (номер и работник из одного общества)
        UniqueConstraint("company_id", "id", name="uq_employees_company_id_id"),
        # Один работник — разные учётки в разных обществах
        UniqueConstraint("user_id", "company_id", name="uq_employees_user_id_company_id"),
        # Табельный номер уникален в рамках общества
        UniqueConstraint("company_id", "personnel_no", name="uq_employees_company_personnel_no"),
        CheckConstraint(
            "fired_at IS NULL OR hired_at IS NULL OR fired_at >= hired_at",
            name="ck_employees_period",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Общество (юрлицо), в котором работает
    company_id: Mapped[int] = mapped_column(
        ForeignKey("shared.companies.id"), index=True
    )

    # Учётная запись (nullable: не у всех работников есть вход в систему)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.users.id"), index=True
    )

    # Кадровые данные
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

    user: Mapped["User | None"] = relationship(back_populates="employee")
    company: Mapped["Company"] = relationship()
