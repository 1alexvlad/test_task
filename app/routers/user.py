from fastapi import APIRouter, Body, Cookie, HTTPException, status, Response, Depends

from models.users import User
from core.dependencies import get_current_user, get_current_admin
from schemas.users import SUserCreate, SUserLogin, SAboutMe, SAccount, SPayment, SToken, STokenData
from services.users import UsersServices
from services.accounts import AccountsServices
from services.payments import PaymentsServices
from services.auth import RefreshTokenService
from core.auth import authenticated_user, create_access_token, get_password_hash



router = APIRouter(prefix="/user", tags=["user"])

@router.post("/register")
async def register_user(user_data: SUserCreate) -> dict:
    existing_user = await UsersServices.find_one_or_none(email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Пользователь с таким email уже существует')
    
    hashed_password = get_password_hash(user_data.password)
    await UsersServices.add(
        email = user_data.email,
        password = hashed_password,
        full_name = user_data.full_name,    
    )
    return {"message": "Пользователь успешно зарегистрирован"}


@router.post("/login")
async def login_user(response: Response, user_data: SUserLogin) -> SToken:
    user = await authenticated_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    
    access_token = create_access_token({'sub': str(user.id), 'role': user.is_admin})
    refresh_token = await RefreshTokenService.create_and_save_refresh_token(user_id=user.id)


    response.set_cookie(
        key="fastapi_access_token", 
        value=access_token, 
        httponly=True, 
        secure=True,         
        samesite="strict",     
        path="/" 
    )

    response.set_cookie(
        key="fastapi_refresh_token", 
        value=refresh_token,
        httponly=True, 
        secure=False, 
        samesite="strict",
        path="/" 
    )



    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }



@router.post('/logout')
async def logout_user(response: Response, fastapi_refresh_token: str | None = Cookie(default=None, alias="fastapi_refresh_token")) -> dict:
    if fastapi_refresh_token:
        await RefreshTokenService.revoke_refresh_token(fastapi_refresh_token)

    response.delete_cookie('fastapi_access_token')
    response.delete_cookie('fastapi_refresh_token')
    
    return {'message': 'Вы успешно вышли'}


@router.get('/me')
async def get_me(current_user: User = Depends(get_current_user)) -> SAboutMe:
    return SAboutMe(id=current_user.id, email=current_user.email, full_name=current_user.full_name)


@router.get('/accounts')
async def get_user_accounts(current_user: User = Depends(get_current_user)) -> list[SAccount]:
    user_accounts = await AccountsServices.find_all(user_id=current_user.id)

    return user_accounts

@router.get('/payments')
async def get_user_paymets(current_user: User = Depends(get_current_user)) -> list[SPayment]:
    user_payments  = await PaymentsServices.find_all(user_id=current_user.id)

    return user_payments 


@router.post("/refresh")
async def refresh_access_token(
    response: Response, 
    fastapi_refresh_token: str | None = Cookie(default=None)
):
    if not fastapi_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh token missing"
        )

    new_refresh, user_id = await RefreshTokenService.rotate_refresh_token(fastapi_refresh_token)

    if new_refresh is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    if new_refresh == "expired":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    user = await UsersServices.find_one_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access = create_access_token({'sub': str(user.id), 'role': user.is_admin})
    
    response.set_cookie(
        key='FastAPI-token', 
        value=new_access, 
        httponly=True,
        samesite="strict"
    )
    
    response.set_cookie(
        key='fastapi_refresh_token',
        value=new_refresh, 
        httponly=True,
        samesite="strict"
    )

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }
