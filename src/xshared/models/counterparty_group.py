from sqlalchemy.orm import Mapped, relationship

from xshared.db import SupplementaryBase


class CounterpartyGroup(SupplementaryBase):
    __tablename__ = "counterparty_groups"

    ca_list: Mapped[list["Counterparty"]] = relationship(
        back_populates="counterpartygroup"
    )
