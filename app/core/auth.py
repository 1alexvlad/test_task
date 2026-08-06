import os

from passlib.context import CryptContext
from pydantic import EmailStr
from datetime import datetime, timedelta, timezone
from jose import jwt

from services.users import UsersServices



SECRET_KEY = '597f373bfa20c4af4023a664cdc4b0fe9c4113ce0457fd6f4013c5edb203e8de'
ALGORITHM = 'HS256'

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticated_user(email: EmailStr, password: str):
    user = await UsersServices.find_one_or_none(email=email)
    if user and verify_password(password, user.password):
        return user
    
    return None

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)  
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt