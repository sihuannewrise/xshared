from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.db import BaseWithPK


class KPP(BaseWithPK):
    __tablename__ = "kpps"
    __table_args__ = (
        CheckConstraint("name ~ '^[0-9]{9}$'", name="name_format"),
    )

    name: Mapped[str] = mapped_column(String(9), unique=True)
    description: Mapped[str | None] = mapped_column(String(100))

    ca_list: Mapped[list["KppCaMapping"]] = relationship(back_populates="kpp")

    def __repr__(self) -> str:
        return f"<KPP ({self.name})>"
