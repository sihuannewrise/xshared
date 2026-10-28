from datetime import date

from sqlalchemy import (
    CheckConstraint, Date, ForeignKey, Index, String, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.db import TimestampedBase


class EmployeeAssignment(TimestampedBase):
    """
    Период работы в должности/отделе.
    Одна запись = одна «версия» условий труда.
    valid_to IS NULL = текущая.
    """
    __tablename__ = "employee_assignments"
    __table_args__ = (
        CheckConstraint(
            "valid_to IS NULL OR valid_to >= valid_from",
            name="period",
        ),
        Index(
            "uq_employee_assignments_current",
            "employee_id",
            unique=True,
            postgresql_where=text("valid_to IS NULL"),
        ),
        Index("ix_employee_assignments_employee_period", "employee_id", "valid_from"),
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("shared.employees.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    position: Mapped[str | None] = mapped_column(String(255))
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("shared.departments.id")
    )
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date)   # NULL = current

    reason: Mapped[str | None] = mapped_column(String(100))

    employee: Mapped["Employee"] = relationship(back_populates="assignments")
    department: Mapped["Department | None"] = relationship(
        back_populates="assignments", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<EmployeeAssignment (employee={self.employee_id}, {self.position})>"
