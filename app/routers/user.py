from fastapi import APIRouter, HTTPException, status, Response, Depends

from models.users import User
from core.dependencies import get_current_user, get_current_admin
from schemas.users import SUserCreate, SUserLogin, SAboutMe, SAccount, SPayment
from services.users import UsersServices
from services.accounts import AccountsServices
from services.payments import PaymentsServices
from core.auth import authenticated_user, create_access_token, get_password_hash



router = APIRouter(prefix="/user")

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
async def login_user(response: Response, user_data: SUserLogin) -> dict:
    user = await authenticated_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    access_token = create_access_token({'sub': str(user.id), 'role': user.is_admin})
    response.set_cookie('FastAPI-token', access_token, httponly=True)
    return {'message': 'Вы вошли'}


@router.post('/logout')
async def logout_user(response: Response) -> dict:
    response.delete_cookie('FastAPI-token')
    return {'message': 'Вы вышли'}

    
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

