from decimal import Decimal  
from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    user: Mapped["User"] = relationship(back_populates="payments")
    account: Mapped["Account"] = relationship(back_populates="payments")
