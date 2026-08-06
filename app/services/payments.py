from models.payments import Payment
from services.base import BaseService


class PaymentsServices(BaseService):
    model = Payment
