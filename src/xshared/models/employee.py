from datetime import date

from sqlalchemy import (
    Boolean, CheckConstraint, Date, ForeignKey, String,
    UniqueConstraint, true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy

from xshared.db import AuditBase


class Employee(AuditBase):
    __tablename__ = "employees"
    __table_args__ = (
        UniqueConstraint("company_id", "id", name="uq_employees_company_id_id"),
        UniqueConstraint("person_id", "company_id", name="uq_employees_person_company"),
        UniqueConstraint("user_id", "company_id", name="uq_employees_user_id_company_id"),
        UniqueConstraint("company_id", "personnel_no", name="uq_employees_company_personnel_no"),
        CheckConstraint(
            "fired_at IS NULL OR hired_at IS NULL OR fired_at >= hired_at",
            name="period",
        ),
    )

    person_id: Mapped[int] = mapped_column(
        ForeignKey("shared.persons.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("shared.companies.id"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.users.id"), index=True
    )

    personnel_no: Mapped[str | None] = mapped_column(String(10))

    hired_at: Mapped[date | None] = mapped_column(Date)
    fired_at: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )

    person: Mapped["Person"] = relationship(back_populates="employees", lazy="selectin")
    company: Mapped["Company"] = relationship(back_populates="employees", lazy="selectin")
    user: Mapped["User | None"] = relationship(back_populates="employee", lazy="selectin", uselist=False)
    assignments: Mapped[list["EmployeeAssignment"]] = relationship(
        back_populates="employee", lazy="selectin",
        order_by="EmployeeAssignment.valid_from.desc()",
    )
    departments = association_proxy("assignments", "department")
