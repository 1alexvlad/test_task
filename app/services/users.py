from models.users import User
from services.base import BaseService


class UsersServices(BaseService):
    model = User
