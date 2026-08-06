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
        from_attribute = True


class AdminUserResponseSchema(BaseModel):
    id: int 
    email: EmailStr
    full_name: str 
    is_admin: bool 

    accounts: list[AdminUserAccountSchema] = []

    class Config: 
        from_attribute = True
