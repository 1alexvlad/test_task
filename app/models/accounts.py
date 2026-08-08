from decimal import Decimal  
from sqlalchemy import text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.users import User
    from models.payments import Payment


class Account(Base):
    __tablename__='accounts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), server_default=text("0.00"))

    user: Mapped["User"] = relationship(back_populates="accounts")
    payments: Mapped[list["Payment"]] = relationship(back_populates="account")