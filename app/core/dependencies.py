import os 
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt

from models.users import User
from services.users import UsersServices



SECRET_KEY = '597f373bfa20c4af4023a664cdc4b0fe9c4113ce0457fd6f4013c5edb203e8de'
ALGORITHM = 'HS256'


def get_toket(request: Request):
    token = request.cookies.get("FastAPI-token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен отсутсвует')
    return token


async def get_current_user(token: str = Depends(get_toket)):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверный формат токена')

    expire: str = payload.get('exp')
    
    current_timestamp = datetime.now(timezone.utc).timestamp()
    if (not expire) or (int(expire) < int(current_timestamp)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен истек')
    
    user_id: str = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user = await UsersServices.find_one_or_none(id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для администраторов",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
