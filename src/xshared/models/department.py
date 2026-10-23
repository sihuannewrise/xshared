# src/xshared/models/department.py
from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.db import SharedBase


class Department(SharedBase):
    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("company_id", "name", name="uq_departments_company_name"),
        UniqueConstraint("company_id", "id", name="uq_departments_company_id_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("shared.companies.id"), index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(String(1000))

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.departments.id"), index=True
    )

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    parent: Mapped[Department | None] = relationship(
        remote_side="Department.id", back_populates="children"
    )
    children: Mapped[list[Department]] = relationship(back_populates="parent")

    company: Mapped["Company"] = relationship()
    employees: Mapped[list["Employee"]] = relationship(back_populates="department")

    def __repr__(self) -> str:
        return f"<Department ({self.name})>"
