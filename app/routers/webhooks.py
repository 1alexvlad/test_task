import hashlib
from fastapi import APIRouter, HTTPException, status

from schemas.users import WebhookPaymentSchema
from services.payments import PaymentsServices
from services.accounts import AccountsServices

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

SECRET_KEY = '597f373bfa20c4af4023a664cdc4b0fe9c4113ce0457fd6f4013c5edb203e8de'


@router.post('/payment')
async def handle_payment_webhook(data: WebhookPaymentSchema):
    amount_normalized = data.amount.normalize()

    if amount_normalized % 1 == 0:
        amount_str = str(int(amount_normalized))
    else:
        amount_str = str(amount_normalized)

    raw_string = f"{data.account_id}{amount_str}{data.transaction_id}{data.user_id}{SECRET_KEY}"
    generated_signature = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()

    if generated_signature != data.signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверная подпись"
        )
    account = await PaymentsServices.process_payment_webhook(
        account_id=data.account_id,
        user_id=data.user_id,
        transaction_id=data.transaction_id,
        amount=data.amount
    )
    if account is None:
        return {
            "status": "success", 
            "message": "Transaction already processed"
        }
    return {
        "status": "success",
        "message": "Payment processed successfully",
        "account_id": account.id,
        "new_balance": float(account.balance)
    }
