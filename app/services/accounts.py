from models.accounts import Account
from services.base import BaseService


class AccountsServices(BaseService):
    model = Account
