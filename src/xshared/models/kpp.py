from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.models._base_entities import TimestampedBase


class KPP(TimestampedBase):
    __tablename__ = "kpps"
    __table_args__ = (
        CheckConstraint("name ~ '^[0-9]{9}$'", name="ck_kpps_name_format"),
    )

    name: Mapped[str] = mapped_column(String(9), unique=True, nullable=False)

    ca_list: Mapped[list["CaKppMapping"]] = relationship(back_populates="kpp")

    def __repr__(self) -> str:
        return f"<KPP ({self.name})>"
