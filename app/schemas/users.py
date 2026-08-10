from pydantic import BaseModel, EmailStr
from decimal import Decimal  



class SUserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class SUserLogin(BaseModel):
    email: EmailStr
    password: str

class SAboutMe(BaseModel):
    id: int
    email: EmailStr
    full_name: str

class SAccount(BaseModel):
    id: int
    user_id: int
    balance: Decimal

    class Config:
        from_attributes = True


class SPayment(BaseModel):
    id: int
    transaction_id: str 
    account_id: int 
    amount: Decimal

    class Config:
        from_attributes = True


class AdminUserAccountSchema(BaseModel):
    id: int
    balance: Decimal

    class Config: 
        from_attributes = True


class AdminUserResponseSchema(BaseModel):
    id: int 
    email: EmailStr
    full_name: str 
    is_admin: bool 

    accounts: list[AdminUserAccountSchema] = []

    class Config: 
        from_attributes = True


class SAdminUsersShow(BaseModel):
    id: int 
    email: EmailStr
    full_name: str 

    accounts: list[SAccount] = []

    class Config: 
        from_attributes = True

class SUserUpdate(BaseModel):
    email: EmailStr | None = None 
    full_name: str | None = None 
    is_admin: str | None = None 
    pasword: str | None = None 

    class Config: 
        from_attributes = True

class WebhookPaymentSchema(BaseModel):
    transaction_id: str 
    account_id: int 
    user_id: int 
    amount: Decimal 
    signature: str

class WebhookResponseSchema(BaseModel):
    status: str
    message: str
    account_id: int | None = None
    new_balance: Decimal | None = None

class SToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class STokenData(BaseModel):
    user_id: int
