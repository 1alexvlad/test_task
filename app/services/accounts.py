from decimal import Decimal

from sqlalchemy import select

from models.accounts import Account
from models.payments import Payment
from services.base import BaseService
from database import async_session_maker


class AccountsServices(BaseService):
    model = Account

    @classmethod
    async def process_payment_webhook(cls, account_id: int, user_id: int, transaction_id: str, amount: Decimal) -> Account:
        async with async_session_maker() as session:
            async with session.begin():

                payment_query = select(Payment).where(Payment.transaction_id == transaction_id)
                payment_result = await session.execute(payment_query)
                existing_payment = payment_result.scalars_one_or_none()

                if existing_payment is not None:
                    return None 

                account_query = select(Account).where(Account.id == account_id, Account.user_id == user_id).with_for_update()
                account_result = await session.execute(account_query)
                account = account_result.scalar_one_or_none()

                if account is None:
                    account = Account(id=account_id, user_id=user_id, balance=amount)
                    session.add(account)
                else:
                    account.balance += amount 

                new_payment = Payment(
                    transaction_id=transaction_id,
                    account_id=account_id,
                    user_id=user_id,
                    amount=amount
                )
                session.add(new_payment)

                await session.refresh(account)
                return account