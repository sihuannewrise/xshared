from datetime import date

from sqlalchemy import Date, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func

from xshared.db import AuditBase


class Person(AuditBase):
    """
    Физическое лицо. Может быть трудоустроено в нескольких обществах
    (через employees) и/или иметь учётную запись (через employees.user_id).
    """
    __tablename__ = "persons"
    __table_args__ = (
        UniqueConstraint(
            "last_name", "first_name", "patronymic_name", "birthdate",
            name="uq_persons_full_name_birthdate",
        ),
    )

    first_name: Mapped[str] = mapped_column(String(100))
    patronymic_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))

    birthdate: Mapped[date | None] = mapped_column(Date)
    social_no: Mapped[str | None] = mapped_column(String(20), unique=True)

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="person", lazy="selectin"
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

    def __repr__(self) -> str:
        return f"<Person ({self.full_name})>"
